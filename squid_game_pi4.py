import time
import random
import subprocess
import cv2
import numpy as np
import pigpio

from gpiozero import LED

# =========================
# CONFIG GPIO (BCM)
# =========================
SERVO_GPIO = 17
LED_RED_GPIO = 16
LED_GREEN_GPIO = 18

MAX_PLAYERS = 7
DETECTION_SECONDS = 3.0
MOTION_THRESHOLD = 0.02
PAD = 120

MUSIC_FILE = "/home/pi/squidgame_audio/music.mp3"  # adapte si besoin

# =========================
# AUDIO (OPTION 1)
# =========================
music_proc = None

def music_on():
    global music_proc
    if music_proc is None:
        # mpg123 joue le mp3 (son via jack/HDMI)
        music_proc = subprocess.Popen(["mpg123", "-q", MUSIC_FILE])

def music_off():
    global music_proc
    if music_proc is not None:
        music_proc.terminate()
        music_proc = None

def say(txt):
    subprocess.run(["espeak-ng", "-v", "fr", txt], check=False)

# =========================
# SERVO via pigpio
# =========================
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio non connecté. Lance: sudo systemctl start pigpiod")

def set_servo_angle(angle):
    angle = max(0, min(180, angle))
    pulse = 500 + (2400 - 500) * (angle / 180.0)
    pi.set_servo_pulsewidth(SERVO_GPIO, pulse)

# =========================
# LEDs
# =========================
led_red = LED(LED_RED_GPIO)
led_green = LED(LED_GREEN_GPIO)

def eyes_red():
    led_green.off()
    led_red.on()

def eyes_green():
    led_red.off()
    led_green.on()

def eyes_off():
    led_red.off()
    led_green.off()

# =========================
# OpenCV ArUco
# =========================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Caméra /dev/video0 non ouverte (VideoCapture(0) échoue).")

aruco = cv2.aruco
dict_aruco = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
detector = aruco.ArucoDetector(dict_aruco, aruco.DetectorParameters())

eliminated = set()

def clamp(x1, y1, x2, y2, w, h):
    x1 = max(0, x1); y1 = max(0, y1)
    x2 = min(w - 1, x2); y2 = min(h - 1, y2)
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2

print("JEU SQUID GAME (RPI 4B) INITIALISÉ")
say("Jeu initialisé.")

try:
    while True:
        # ============ FEU VERT ============
        print("🎵 FEU VERT - MUSIQUE")
        set_servo_angle(0)
        music_on()
        eyes_green()
        time.sleep(random.uniform(3, 6))

        # ============ FEU ROUGE ============
        print("🔴 FEU ROUGE - SURVEILLANCE")
        music_off()
        eyes_red()
        set_servo_angle(180)
        time.sleep(0.4)

        start = time.time()
        prev = None

        while (time.time() - start) < DETECTION_SECONDS:
            ok, frame = cap.read()
            if not ok:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if prev is None:
                prev = gray
                continue

            diff = cv2.absdiff(gray, prev)
            _, mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

            corners, ids, _ = detector.detectMarkers(gray)

            if ids is not None:
                ids = ids.flatten()
                h, w = gray.shape[:2]

                for c, pid in zip(corners, ids):
                    if pid < 1 or pid > MAX_PLAYERS:
                        continue
                    if pid in eliminated:
                        continue

                    pts = c[0]
                    x1, x2 = int(pts[:, 0].min()), int(pts[:, 0].max())
                    y1, y2 = int(pts[:, 1].min()), int(pts[:, 1].max())

                    roi = clamp(x1 - PAD, y1 - PAD, x2 + PAD, y2 + PAD, w, h)
                    if roi is None:
                        continue

                    rx1, ry1, rx2, ry2 = roi
                    region = mask[ry1:ry2, rx1:rx2]
                    motion_ratio = (region > 0).mean()

                    if motion_ratio > MOTION_THRESHOLD:
                        eliminated.add(pid)
                        print(f"💀 ELIMINÉ: joueur {pid} (motion={motion_ratio:.3f})")

                        # annonce
                        say(f"Numéro {pid}, t'as bougé, t'es éliminé.")

                        # mouvement tête "non"
                        for a in (120, 180, 130, 180):
                            set_servo_angle(a)
                            time.sleep(0.15)

            prev = gray

        eyes_off()
        time.sleep(0.6)

except KeyboardInterrupt:
    print("Stop (CTRL+C)")

finally:
    music_off()
    pi.set_servo_pulsewidth(SERVO_GPIO, 0)
    pi.stop()
    cap.release()
    eyes_off()
