import socket
import json
import time
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8765

metrics = {"rx_bytes": 0, "tx_bytes": 0, "requests": 0, "errors": 0, "uptime_s": 0}
start = time.time()

def main():
    print("seriald started")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print("IPC listening on 127.0.0.1:8765")
    while True:
        conn, addr = s.accept()
        with conn:
            f_r = conn.makefile("rb")
            f_w = conn.makefile("wb")
            while True:
                line = f_r.readline()
                if not line:
                    break
                metrics["rx_bytes"] += len(line)
                try:
                    req = json.loads(line.decode("utf-8"))
                    rid = req.get("id")
                    method = req.get("method")
                    metrics["uptime_s"] = int(time.time() - start)
                    if method == "ping":
                        metrics["requests"] += 1
                        result = {"pong": True}
                        resp = {"id": rid, "ok": True, "result": result}
                    elif method == "get_status":
                        metrics["requests"] += 1
                        result = {
                            "model": "1.5KT",
                            "connected": False,
                            "ts": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "data": {"note": "dummy"},
                        }
                        resp = {"id": rid, "ok": True, "result": result}
                    elif method == "get_metrics":
                        metrics["requests"] += 1
                        resp = {"id": rid, "ok": True, "result": metrics}
                    else:
                        metrics["errors"] += 1
                        resp = {
                            "id": rid,
                            "ok": False,
                            "error": {"code": "unknown_method", "message": "unknown method"},
                        }
                except Exception:
                    metrics["errors"] += 1
                    rid = None
                    resp = {
                        "id": rid,
                        "ok": False,
                        "error": {"code": "bad_request", "message": "invalid request"},
                    }
                out = (json.dumps(resp) + "\n").encode("utf-8")
                try:
                    f_w.write(out)
                    f_w.flush()
                    metrics["tx_bytes"] += len(out)
                except Exception:
                    break

if __name__ == "__main__":
    main()
