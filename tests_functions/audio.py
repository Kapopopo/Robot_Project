from time import sleep
import pigpio, subprocess

pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("pigpiod non lancé")

def set_servo_angle(a):
    pi.set_servo_pulsewidth(17, 500 + (2400-500)*(a/180))

def play_elim():
    subprocess.run(["aplay","/home/pi/sounds/eliminate.wav"])

def say_robot(t):
    subprocess.run(["espeak-ng","-v","fr","-s","120","-p","35",t])

print("TEST ÉLIMINATION")
set_servo_angle(180)
play_elim()
sleep(0.6)
say_robot("Numéro 3. T'as bougé. T'es éliminé.")
