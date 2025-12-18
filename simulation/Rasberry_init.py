import cv2, time
import subprocess
from machine import Pin, PWM
from time import sleep, ticks_ms, ticks_diff
import random

# ===== SERVO =====
servo = PWM(Pin(17))
servo.freq(50)

def set_angle(angle):
    min_us = 500
    max_us = 2400
    us = int(min_us + (max_us - min_us) * (angle / 180))
    duty = int(us * 65535 / 20000)
    servo.duty_u16(duty)

# ===== PIR =====
pir = Pin(4, Pin.IN)

# ===== LED YEUX =====
led_red = Pin(16, Pin.OUT)
led_green = Pin(18, Pin.OUT)

# ===== BUZZER (musique) =====
buzzer = Pin(15, Pin.OUT)

def music_on():
    buzzer.on()

def music_off():
    buzzer.off()

def eyes_red():
    led_green.off()
    led_red.on()

def eyes_green():
    led_red.off()
    led_green.on()

def eyes_off():
    led_red.off()
    led_green.off()

def wait_for_motion(timeout_s):
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < int(timeout_s * 1000):
        if pir.value() == 1:
            return True
        sleep(0.02)
    return False

print("JEU SQUID GAME INITIALISÉ")

while True:

    # ================= FEU VERT =================
    print("FEU VERT - MUSIQUE")
    set_angle(0)
    music_on()
    eyes_green()

    sleep(random.uniform(3, 6))

    # ================= ROTATION =================
    print("ROTATION - FEU ROUGE")
    music_off()
    eyes_red()

    set_angle(180)
    sleep(0.5)

    # ================= DÉTECTION =================
    print("SURVEILLANCE")
    if wait_for_motion(3):
        print("ÉLIMINÉ")

        eyes_red()
        music_on()      # son d’élimination
        sleep(1)
        music_off()

        # mouvement tête "non"
        set_angle(120)
        sleep(0.15)
        set_angle(180)
        sleep(0.15)
        set_angle(130)
        sleep(0.15)
        set_angle(180)
        sleep(0.15)


    else:
        print("PERSONNE N'A BOUGÉ")
        eyes_green()
        sleep(1)

    eyes_off()
    sleep(1)