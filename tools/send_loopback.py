import sys, time
import serial

port = sys.argv[1] if len(sys.argv) > 1 else "COM16"
baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

payload = b"HELLO_SPE_LOOPBACK\r\n"

with serial.Serial(port=port, baudrate=baud, timeout=1) as s:
    for _ in range(10):
        s.write(payload)
        s.flush()
        time.sleep(0.1)

print("sent", payload, "to", port, "baud", baud)
