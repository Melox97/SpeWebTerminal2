import socket
import threading
import time

import pytest

import apps.ipc as ipc
from apps.config import IPC_CALL_TIMEOUT_S_DEFAULT


def slow_server(host, port, ready):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind((host, port))
    srv.listen(1)
    ready.set()

    conn, _ = srv.accept()

    # read request
    conn.recv(4096)

    # do NOT respond (simulate dead daemon)
    time.sleep(IPC_CALL_TIMEOUT_S_DEFAULT + 0.3)

    conn.close()
    srv.close()


def test_ipc_timeout(monkeypatch):

    host = "127.0.0.1"

    # get free port
    s = socket.socket()
    s.bind((host, 0))
    port = s.getsockname()[1]
    s.close()

    ready = threading.Event()

    t = threading.Thread(
        target=slow_server,
        args=(host, port, ready),
        daemon=True
    )

    t.start()
    ready.wait()
    
    orig_create = ipc.socket.create_connection

    def _patched_create_connection(_addr, timeout=None):
        return orig_create((host, port), timeout=timeout)

    monkeypatch.setattr(ipc.socket, "create_connection", _patched_create_connection)