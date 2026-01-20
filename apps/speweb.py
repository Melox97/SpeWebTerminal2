import subprocess
import sys
import os
import time
import argparse
import threading

def stream_reader(pipe, file_obj, prefix=""):
    try:
        for line in iter(pipe.readline, b""):
            line_str = line.decode("utf-8", errors="replace")
            # Write to console
            sys.stdout.write(f"{prefix}{line_str}")
            sys.stdout.flush()
            # Write to file
            if file_obj:
                try:
                    file_obj.write(f"{prefix}{line_str}")
                    file_obj.flush()
                except ValueError:
                    pass # File might be closed
    except Exception:
        pass

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

    # Setup logging
    log_dir = os.path.join(os.getcwd(), "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "runtime.log")
    log_file = open(log_file_path, "a", buffering=1)
    
    print(f"Logging to console and {log_file_path}")

    print("Starting serial daemon")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    serial_path = os.path.join(script_dir, "seriald.py")
    http_path = os.path.join(script_dir, "httpd.py")
    
    serial_proc = subprocess.Popen(
        [sys.executable, serial_path], 
        env=env,
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT
    )
    t_serial = threading.Thread(target=stream_reader, args=(serial_proc.stdout, log_file, "[SERIAL] "))
    t_serial.daemon = True
    t_serial.start()

    print("Starting HTTP service")
    http_proc = subprocess.Popen(
        [sys.executable, http_path], 
        env=env,
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT
    )
    t_http = threading.Thread(target=stream_reader, args=(http_proc.stdout, log_file, "[HTTP] "))
    t_http.daemon = True
    t_http.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping services...")
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
        
        if log_file:
            log_file.close()

if __name__ == "__main__":
    main()
