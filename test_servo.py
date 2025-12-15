import time
import pigpio

SERVO_GPIO = 17

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio non lancé")

def set_angle(angle):
    pulse = 500 + (2400 - 500) * (angle / 180)
    pi.set_servo_pulsewidth(SERVO_GPIO, pulse)

try:
    while True:
        set_angle(0)
        time.sleep(1)
        set_angle(90)
        time.sleep(1)
        set_angle(180)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    pi.set_servo_pulsewidth(SERVO_GPIO, 0)
    pi.stop()
