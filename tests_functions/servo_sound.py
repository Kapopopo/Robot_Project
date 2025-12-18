import time
import pigpio, subprocess

SERVO_GPIO = 17


pi = pigpio.pi()
pi.set_mode(SERVO_GPIO, pigpio.OUTPUT)

if not pi.connected:
    raise RuntimeError("pigpio non lancé")

while True:
    aplay = subprocess.Popen(["aplay", "-D", "hw:2,0", "../sounds/pain.wav"])
    time.sleep(2)
    aplay.terminate()
    pi.set_servo_pulsewidth(SERVO_GPIO, 700)
    time.sleep(1)
    pi.set_servo_pulsewidth(SERVO_GPIO, 2300)
    time.sleep(5)
    pi.set_servo_pulsewidth(SERVO_GPIO, 700)