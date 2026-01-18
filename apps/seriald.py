import json
import os
import socket
import threading
import time
from datetime import datetime, timezone


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

        self._stop = threading.Event()

    def uptime_s(self) -> int:
        return int(time.time() - self.start_ts)

    def _ok(self, req_id: int, result: dict) -> dict:
        return {"id": req_id, "ok": True, "result": result}

    def _err(self, req_id: int, code: str, message: str) -> dict:
        self.metrics["errors"] += 1
        self.state["last_error"] = code
        return {"id": req_id, "ok": False, "error": {"code": code, "message": message}}

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


def main() -> None:
    SerialDaemon().serve_forever()


if __name__ == "__main__":
    main()
