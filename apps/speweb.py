import subprocess
import sys
import os
import time

def main():
    print("Starting serial daemon")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    serial_path = os.path.join(script_dir, "seriald.py")
    http_path = os.path.join(script_dir, "httpd.py")
    serial_proc = subprocess.Popen([sys.executable, serial_path])
    print("Starting HTTP service")
    http_proc = subprocess.Popen([sys.executable, http_path])
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
