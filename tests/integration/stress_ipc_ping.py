import json
import socket
import subprocess
import sys
import time
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8765
REQUESTS = 1000


def repo_root():
    return Path(__file__).resolve().parents[2]


def wait_for_port(proc, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            raise RuntimeError("Daemon exited early")
        try:
            with socket.create_connection((HOST, PORT), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Daemon did not start in time")


def main():
    print(f"Starting stress test: {REQUESTS} ping requests")

    proc = subprocess.Popen(
        [sys.executable, "-m", "apps.seriald"],
        cwd=str(repo_root()),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_port(proc)

        start = time.time()
        errors = 0

        with socket.create_connection((HOST, PORT), timeout=5.0) as sock:
            for i in range(REQUESTS):
                req = {"id": i, "method": "ping"}
                sock.sendall((json.dumps(req) + "\n").encode("utf-8"))
                data = sock.recv(4096)
                resp = json.loads(data.decode("utf-8").strip())

                if not resp.get("ok"):
                    errors += 1

        duration = time.time() - start
        print(f"Completed in {duration:.2f}s")
        print(f"Errors: {errors}")

        if errors > 0:
            raise RuntimeError("Stress test failed: errors detected")

    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    main()
