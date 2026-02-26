import json
import os
import socket
import threading
import time
import serial
import base64
from collections import deque
from datetime import datetime, timezone

from apps.serial_error import make_serial_error
from apps.serial_error_store import ErrorStore
from apps.config import SERIAL_TIMEOUT_S_DEFAULT


def _utc_iso_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SerialDaemon:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port

        self.start_ts = time.time()
        self.metrics = {
            "rx_bytes": 0,
            "tx_bytes": 0,
            "requests": 0,
            "errors": 0,
        }

        self.state = {
            "model": "1.5KT",
            "connected": False,
            "last_error": None,
        }

        self.errors = ErrorStore()

        # Serial configuration from environment
        env_port = os.getenv("SPE_SERIAL_PORT")
        env_baud = os.getenv("SPE_SERIAL_BAUD", "115200")

        self.serial_port = (env_port or "").strip() or None
        try:
            self.serial_baud = int(env_baud)
        except ValueError:
            self.serial_baud = 115200

        self.state["serial"] = {
            "port": self.serial_port,
            "baud": self.serial_baud,
            "last_probe_ts": None,
            "is_open": False,
            "last_open_ts": None,
            "last_close_ts": None,
            "last_rx_ts": None,
            "last_tx_ts": None,
        }

        self._stop = threading.Event()
        self._reader_stop = threading.Event()
        self._ser_lock = threading.Lock()
        self._ser = None
        self._reader_thread = None
        self._ring = deque(maxlen=50)

    def uptime_s(self) -> int:
        return int(time.time() - self.start_ts)

    def _ok(self, req_id: int, result: dict) -> dict:
        return {"id": req_id, "ok": True, "result": result}

    def _err(self, req_id: int, code: str, message: str) -> dict:
        self.metrics["errors"] += 1
        self.state["last_error"] = code
        return {"id": req_id, "ok": False, "error": {"code": code, "message": message}}

    def _record_error(
        self,
        *,
        kind: str,
        op: str,
        retryable: bool,
        detail: str | None = None,
        tx: bytes | None = None,
        rx: bytes | None = None,
    ) -> None:
        err = make_serial_error(
            layer="serial",
            kind=kind,
            op=op,
            retryable=retryable,
            port=self.serial_port,
            baud=self.serial_baud,
            timeout_s=SERIAL_TIMEOUT_S_DEFAULT,
            tx=tx,
            rx=rx,
            detail=detail,
        )
        self.errors.add(err)
        self.state["last_error"] = f"{err['layer']}:{err['kind']}:{err['op']}"

    def handle(self, req: dict) -> dict:
        if not isinstance(req, dict):
            return self._err(-1, "invalid_request", "Request must be a JSON object")

        if "id" not in req or "method" not in req:
            rid = req.get("id", -1) if isinstance(req.get("id", -1), int) else -1
            return self._err(rid, "invalid_request", "Missing required fields: id, method")

        req_id = req["id"]
        method = req["method"]

        if not isinstance(req_id, int) or not isinstance(method, str):
            rid = req_id if isinstance(req_id, int) else -1
            return self._err(rid, "invalid_request", "Invalid types for id/method")

        self.metrics["requests"] += 1

        if method == "ping":
            return self._ok(req_id, {"pong": True})

        if method == "get_status":
            return self._ok(
                req_id,
                {
                    "model": self.state["model"],
                    "connected": bool(self.state["connected"]),
                    "ts": _utc_iso_z(),
                    "data": {"note": "dummy"},
                },
            )

        if method == "get_metrics":
            return self._ok(
                req_id,
                {
                    "rx_bytes": int(self.metrics["rx_bytes"]),
                    "tx_bytes": int(self.metrics["tx_bytes"]),
                    "requests": int(self.metrics["requests"]),
                    "errors": int(self.metrics["errors"]),
                    "uptime_s": int(self.uptime_s()),
                },
            )

        if method == "get_serial_config":
            return self._ok(req_id, {"port": self.serial_port, "baud": self.serial_baud})

        if method == "serial_probe":
            self.state["serial"]["port"] = self.serial_port
            self.state["serial"]["baud"] = self.serial_baud
            self.state["serial"]["last_probe_ts"] = _utc_iso_z()

            if not self.serial_port:
                self.state["connected"] = False
                self.state["last_error"] = "serial_not_configured"
                return self._err(req_id, "serial_not_configured", "Serial port not configured")

            try:
                s = serial.Serial(self.serial_port, self.serial_baud, timeout=SERIAL_TIMEOUT_S_DEFAULT)
                s.close()
                self.state["connected"] = True
                self.state["last_error"] = None
                return self._ok(
                    req_id,
                    {
                        "success": True,
                        "port": self.serial_port,
                        "baud": self.serial_baud,
                        "error": None,
                    },
                )
            except Exception as e:
                self.state["connected"] = False
                self.state["last_error"] = "serial_open_failed"
                return self._ok(
                    req_id,
                    {
                        "success": False,
                        "port": self.serial_port,
                        "baud": self.serial_baud,
                        "error": f"serial_open_failed: {str(e)}",
                    },
                )

        # Persistent open
        if method == "serial_open":
            self.state["serial"]["port"] = self.serial_port
            self.state["serial"]["baud"] = self.serial_baud
            if not self.serial_port:
                self.state["connected"] = False
                self.state["last_error"] = "serial_not_configured"
                return self._err(req_id, "serial_not_configured", "Serial port not configured")

            with self._ser_lock:
                if self.state["serial"]["is_open"] and self._ser is not None:
                    return self._ok(
                        req_id,
                        {
                            "is_open": True,
                            "port": self.serial_port,
                            "baud": self.serial_baud,
                        },
                    )
                try:
                    self._ser = serial.Serial(self.serial_port, self.serial_baud, timeout=SERIAL_TIMEOUT_S_DEFAULT)
                    self.state["serial"]["is_open"] = True
                    self.state["connected"] = True
                    self.state["last_error"] = None
                    ts = _utc_iso_z()
                    self.state["serial"]["last_open_ts"] = ts
                    self._reader_stop.clear()
                    if not self._reader_thread or not self._reader_thread.is_alive():
                        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
                        self._reader_thread.start()
                    return self._ok(
                        req_id,
                        {
                            "is_open": True,
                            "port": self.serial_port,
                            "baud": self.serial_baud,
                        },
                    )
                except Exception as e:
                    self._ser = None
                    self.state["serial"]["is_open"] = False
                    self.state["connected"] = False
                    self.state["last_error"] = "serial_open_failed"
                    return self._err(req_id, "serial_open_failed", str(e))

        if method == "serial_close":
            with self._ser_lock:
                self._reader_stop.set()
                if self._reader_thread and self._reader_thread.is_alive():
                    self._reader_thread.join(timeout=1.0)
                try:
                    if self._ser is not None:
                        try:
                            self._ser.close()
                        except Exception:
                            pass
                        self._ser = None
                    self.state["serial"]["is_open"] = False
                    self.state["connected"] = False
                    ts = _utc_iso_z()
                    self.state["serial"]["last_close_ts"] = ts
                    return self._ok(req_id, {"is_open": False})
                finally:
                    self._reader_thread = None

        if method == "serial_recent":
            params = req.get("params") or {}
            n = params.get("n", 50)
            try:
                n = int(n)
            except Exception:
                n = 50
            items = list(self._ring)[-n:]
            return self._ok(req_id, {"items": items})

        if method == "serial_write":
            params = req.get("params") or {}
            data = params.get("data", "")
            encoding = params.get("encoding", "utf-8")
            with self._ser_lock:
                if not self.state["serial"]["is_open"] or self._ser is None:
                    return self._err(req_id, "serial_not_open", "Serial not open")
                try:
                    payload = (str(data) + "\n").encode(encoding)
                    self._ser.write(payload)
                    self.metrics["tx_bytes"] += len(payload)
                    self.state["serial"]["last_tx_ts"] = _utc_iso_z()
                    return self._ok(req_id, {"written": len(payload)})
                except Exception as e:
                    # record error for diagnostics
                    self._record_error(
                        kind="write_failed",
                        op="serial_write",
                        retryable=True,
                        detail=str(e),
                        tx=payload if "payload" in locals() else None,
                    )
                    return self._err(req_id, "serial_write_failed", str(e))

        return self._err(req_id, "unknown_method", f"Unknown method: {method}")

    def serve_forever(self) -> None:
        print(
            f"seriald started. PID: {os.getpid()}, Start Time (UTC): "
            f"{datetime.now(timezone.utc).isoformat()}"
        )
        print(f"IPC listening on {self.host}:{self.port}")

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(50)
        srv.settimeout(0.5)

        try:
            while not self._stop.is_set():
                try:
                    conn, _addr = srv.accept()
                except socket.timeout:
                    continue

                with conn:
                    conn.settimeout(0.5)
                    buf = b""
                    while not self._stop.is_set():
                        try:
                            chunk = conn.recv(4096)
                        except socket.timeout:
                            break
                        if not chunk:
                            break

                        self.metrics["rx_bytes"] += len(chunk)
                        buf += chunk

                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            if not line.strip():
                                continue

                            try:
                                req = json.loads(line.decode("utf-8"))
                            except Exception:
                                resp = self._err(-1, "invalid_request", "Invalid JSON")
                                out = (json.dumps(resp) + "\n").encode("utf-8")
                                conn.sendall(out)
                                self.metrics["tx_bytes"] += len(out)
                                print("Method: <parse>, Outcome: error")
                                continue

                            method = req.get("method")
                            resp = self.handle(req)
                            outcome = "ok" if resp.get("ok") else "error"
                            print(f"Method: {method}, Outcome: {outcome}")

                            out = (json.dumps(resp) + "\n").encode("utf-8")
                            conn.sendall(out)
                            self.metrics["tx_bytes"] += len(out)
        finally:
            srv.close()

    def _reader_loop(self) -> None:
        print("serial reader thread started")
        while not self._reader_stop.is_set():
            with self._ser_lock:
                ser = self._ser
            if ser is None:
                time.sleep(0.05)
                continue
            try:
                chunk = ser.read(1024)
            except Exception:
                time.sleep(0.05)
                continue
            if chunk:
                self.metrics["rx_bytes"] += len(chunk)
                ts = _utc_iso_z()
                self.state["serial"]["last_rx_ts"] = ts
                b64 = base64.b64encode(chunk).decode("ascii")
                self._ring.append({"ts": ts, "data_b64": b64})
            else:
                # respect timeout pacing
                pass
        print("serial reader thread stopped")


def main() -> None:
    SerialDaemon().serve_forever()


if __name__ == "__main__":
    main()