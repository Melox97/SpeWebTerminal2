import subprocess
import sys
import os
import time
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Serial port")
    parser.add_argument("--baud", type=int, help="Baud rate")
    args = parser.parse_args()

    env = os.environ.copy()
    if args.port:
        env["SPE_SERIAL_PORT"] = args.port
    if args.baud:
        env["SPE_SERIAL_BAUD"] = str(args.baud)

    print("Starting serial daemon")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    serial_path = os.path.join(script_dir, "seriald.py")
    http_path = os.path.join(script_dir, "httpd.py")
    serial_proc = subprocess.Popen([sys.executable, serial_path], env=env)
    print("Starting HTTP service")
    http_proc = subprocess.Popen([sys.executable, http_path], env=env)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        serial_proc.terminate()
        http_proc.terminate()
        try:
            serial_proc.wait(timeout=5)
        except Exception:
            serial_proc.kill()
        try:
            http_proc.wait(timeout=5)
        except Exception:
            http_proc.kill()

if __name__ == "__main__":
    main()
