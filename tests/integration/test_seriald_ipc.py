import json
import socket
import subprocess
import sys
import time
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8765  # default SerialDaemon port


def _repo_root() -> Path:
    # tests/integration/test_*.py -> repo root is 2 parents up
    return Path(__file__).resolve().parents[2]


def _wait_for_port_or_crash(proc: subprocess.Popen, host: str, port: int, timeout: float = 5.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
            raise RuntimeError(f"Daemon exited early.\n{stderr}")

        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)

    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    raise RuntimeError(f"Daemon did not start in time.\n{stderr}")


def test_ping_smoke():
    proc = subprocess.Popen(
        [sys.executable, "-m", "apps.seriald"],
        cwd=str(_repo_root()),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        _wait_for_port_or_crash(proc, HOST, PORT, timeout=5.0)

        with socket.create_connection((HOST, PORT), timeout=2.0) as sock:
            req = {"id": 1, "method": "ping"}
            sock.sendall((json.dumps(req) + "\n").encode("utf-8"))

            data = sock.recv(4096)
            resp = json.loads(data.decode("utf-8").strip())

            assert resp["ok"] is True
            assert resp["result"]["pong"] is True
    finally:
        proc.terminate()
        proc.wait(timeout=5)
