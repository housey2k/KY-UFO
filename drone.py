import socket
import subprocess
import threading
import time
import msvcrt

DRONE_IP = "192.168.1.1"
UDP_PORT = 7099
RTSP_URL = f"rtsp://{DRONE_IP}:7070/webcam"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def start_ffplay():
    return subprocess.Popen([
        "ffplay",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-framedrop",
        "-rtsp_transport", "udp",
        RTSP_URL
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL)

def heartbeat():
    while True:
        try:
            sock.sendto(b"\x01\x01", (DRONE_IP, UDP_PORT))
            time.sleep(1)
        except:
            break

print("Starting video stream...")
ffplay = start_ffplay()

threading.Thread(target=heartbeat, daemon=True).start()

cam = 1
print("\nControls:")
print("  C = switch camera")
print("  Q = quit\n")

try:
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().lower()

            if key == b'c':
                print("Switching camera...")

                # stop ffplay (matches Android app behavior)
                ffplay.terminate()
                ffplay.wait(timeout=2)

                if cam == 1:
                    sock.sendto(b"\x06\x02", (DRONE_IP, UDP_PORT))
                    cam = 2
                else:
                    sock.sendto(b"\x06\x01", (DRONE_IP, UDP_PORT))
                    cam = 1

                # firmware delay (~600ms in app)
                time.sleep(0.6)

                # restart stream
                ffplay = start_ffplay()
                print(f"Camera {cam} active")

            elif key == b'q':
                break

        time.sleep(0.05)

finally:
    ffplay.terminate()
    sock.close()
