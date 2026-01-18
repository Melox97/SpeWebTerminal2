import socket
import json
import time

HOST = "127.0.0.1"
PORT = 8765

def request(method, params=None, timeout=0.5):
    if params is None:
        params = {}
    req = {"id": int(time.time() * 1000), "method": method, "params": params}
    s = socket.create_connection((HOST, PORT), timeout=timeout)
    s.settimeout(timeout)
    f_r = s.makefile("rb")
    f_w = s.makefile("wb")
    data = (json.dumps(req) + "\n").encode("utf-8")
    f_w.write(data)
    f_w.flush()
    line = f_r.readline()
    s.close()
    if not line:
        raise ConnectionError("no response")
    return json.loads(line.decode("utf-8"))
