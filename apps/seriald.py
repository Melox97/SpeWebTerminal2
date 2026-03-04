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
from apps.config import (
    IPC_HOST_DEFAULT,
    IPC_PORT_DEFAULT,
    SERIAL_TIMEOUT_S_DEFAULT,
)

def _utc_iso_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SerialDaemon:
    def __init__(self, host: str = IPC_HOST_DEFAULT, port: int = IPC_PORT_DEFAULT) -> None:
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
        }

        self.recent = deque(maxlen=200)

    def uptime_s(self) -> float:
        return time.time() - self.start_ts

    def _ok(self, req_id: int, result: dict) -> dict:
        return {"ok": True, "id": req_id, "result": result}

    def _err(self, req_id: int, code: str, message: str, details: dict | None = None) -> dict:
        self.metrics["errors"] += 1
        payload = {"code": code, "message": message}
        if details:
            payload["details"] = details
        return {"ok": False, "id": req_id, "error": payload}

    def _serial_err(
        self,
        op: str,
        kind: str,
        message: str,
        *,
        tx: bytes | None = None,
        rx: bytes | None = None,
        detail: dict | None = None,
    ) -> None:
        err = make_serial_error(
            op=op,
            kind=kind,
            message=message,
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
            try:
                return self._ok(
                    req_id,
                    {
                        "model": self.state["model"],
                        "connected": bool(self.state["connected"]),
                        "ts": _utc_iso_z(),
                        "data": {"note": "dummy"},
                    },
                )
            except TimeoutError:
                time.sleep(0.05)
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

                self._serial_err(
                    "probe",
                    "open_failed",
                    "Probe failed",
                    detail={"exc": str(e)},
                )

                return self._err(
                    req_id,
                    "serial_open_failed",
                    "Failed to open serial port",
                    {"exc": str(e)},
                )

        if method == "serial_recent":

            params = req.get("params", {}) or {}
            n = int(params.get("n", 50))
            n = max(1, min(200, n))

            items = list(self.recent)[-n:]

            return self._ok(req_id, {"items": items, "n": n})

        if method == "serial_write":

            params = req.get("params", {}) or {}

            if not isinstance(params, dict):
                return self._err(req_id, "invalid_params", "params must be an object")

            data = params.get("data", "")

            if not isinstance(data, str):
                return self._err(req_id, "invalid_params", "data must be a string")

            try:
                raw = base64.b64decode(data.encode("utf-8"), validate=True)
            except Exception:
                raw = data.encode("utf-8", errors="replace")

            self.recent.append(
                {
                    "ts": _utc_iso_z(),
                    "dir": "tx",
                    "data": raw.hex(),
                }
            )

            self.metrics["tx_bytes"] += len(raw)

            return self._ok(req_id, {"written": len(raw)})

        return self._err(req_id, "unknown_method", f"Unknown method: {method}")

    def serve_forever(self) -> None:

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        srv.bind((self.host, self.port))
        srv.listen(5)

        srv.settimeout(0.5)

        print(f"[seriald] listening on {self.host}:{self.port}")

        while True:

            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue

            conn.settimeout(0.5)

            t = threading.Thread(
                target=self._handle_conn,
                args=(conn, addr),
                daemon=True,
            )

            t.start()

    def _handle_conn(self, conn: socket.socket, addr) -> None:

        try:

            f_r = conn.makefile("rb")
            f_w = conn.makefile("wb")

            while True:

                line = f_r.readline()

                if not line:
                    break

                self.metrics["rx_bytes"] += len(line)

                try:
                    req = json.loads(line.decode("utf-8"))
                except Exception:

                    resp = self._err(-1, "invalid_json", "Malformed JSON")

                    f_w.write((json.dumps(resp) + "\n").encode("utf-8"))
                    f_w.flush()

                    continue

                try:
                    resp = self.handle(req)
                except Exception as e:

                    resp = self._err(
                        req.get("id", -1) if isinstance(req, dict) else -1,
                        "internal_error",
                        str(e),
                    )

                f_w.write((json.dumps(resp) + "\n").encode("utf-8"))
                f_w.flush()

        finally:

            try:
                conn.close()
            except Exception:
                pass


def main() -> None:
    d = SerialDaemon()
    d.serve_forever()


if __name__ == "__main__":
    main()