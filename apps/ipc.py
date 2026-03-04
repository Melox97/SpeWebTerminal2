import socket
import json
import time

from apps.config import IPC_HOST_DEFAULT, IPC_PORT_DEFAULT, IPC_CALL_TIMEOUT_S_DEFAULT

HOST = IPC_HOST_DEFAULT
PORT = IPC_PORT_DEFAULT

def request(method, params=None, timeout=IPC_CALL_TIMEOUT_S_DEFAULT):
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
