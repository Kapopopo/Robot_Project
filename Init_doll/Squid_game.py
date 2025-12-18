from flask import Flask, Response, redirect, request
import cv2, time, numpy as np
import threading, random, subprocess
import pigpio

app = Flask(__name__)

AUDIO_DEVICE = "hw:2,0"
SOUNDS = {
    "ready": "./sounds/ready.wav",
    1: "./sounds/joueur1_elimine.wav",
    2: "./sounds/joueur2_elimine.wav",
    3: "./sounds/joueur3_elimine.wav",
    4: "./sounds/joueur4_elimine.wav",
    "music": "./sounds/pain.wav",
}

def play_wav(path: str):
    subprocess.run(
        ["aplay", "-D", AUDIO_DEVICE, path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def start_music_loop(path: str):
    return subprocess.Popen(
        ["aplay", "-D", AUDIO_DEVICE, path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def stop_process(p):
    if p is None:
        return
    try:
        p.terminate()
        p.wait(timeout=1)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass

SERVO_GPIO = 17
SERVO_0 = 700
SERVO_180 = 2300

pi = pigpio.pi()
pi.set_mode(SERVO_GPIO, pigpio.OUTPUT)
if not pi.connected:
    raise RuntimeError("pigpio non lancé (sudo pigpiod)")

def servo_to_0():
    pi.set_servo_pulsewidth(SERVO_GPIO, SERVO_0)

def servo_to_180():
    pi.set_servo_pulsewidth(SERVO_GPIO, SERVO_180)

WIDTH, HEIGHT = 1280, 720
CAM_DEVICE = 0

cap = cv2.VideoCapture(CAM_DEVICE, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
time.sleep(1)

BLUR_SIZE = (11, 11)
PIXEL_THRESHOLD = 18
ZONE_PIXEL_TRIGGER = 2000
COOLDOWN_SEC = 1.5
prev_gray = None

NUM_PLAYERS = 4
PLAYER_NAMES = {1:"Joueur 1", 2:"Joueur 2", 3:"Joueur 3", 4:"Joueur 4"}

DETECTION_ACTIVE = False
GAME_RUNNING = False
LAST_ELIM_TIME = 0.0
ELIM_LOCK = threading.Lock()

def get_zones(width, n):
    zone_w = width // n
    return [(i * zone_w, (i + 1) * zone_w if i < n - 1 else width) for i in range(n)]

def eliminate_player(player_id: int):
    global LAST_ELIM_TIME
    now = time.time()

    with ELIM_LOCK:
        if now - LAST_ELIM_TIME < COOLDOWN_SEC:
            return
        LAST_ELIM_TIME = now

    wav = SOUNDS.get(player_id)
    if wav:
        play_wav(wav)

def game_loop():
    """
    Boucle principale du jeu:
    - annonce ready
    - alternance random :
        * GO: servo 0 + musique ON + detection OFF
        * STOP: servo 180 + musique OFF + detection ON
    """
    global DETECTION_ACTIVE, GAME_RUNNING

    servo_to_0()
    DETECTION_ACTIVE = False

    try:
        play_wav(SOUNDS["ready"])
    except Exception:
        pass

    music_proc = None
    GAME_RUNNING = True

    try:
        while GAME_RUNNING:
            DETECTION_ACTIVE = False
            servo_to_0()

            music_proc = start_music_loop(SOUNDS["music"])
            go_time = random.uniform(2.0, 6.0)
            time.sleep(go_time)

            stop_process(music_proc)
            music_proc = None

            servo_to_180()
            DETECTION_ACTIVE = True

            stop_time = random.uniform(2.0, 5.0)
            time.sleep(stop_time)

    finally:
        DETECTION_ACTIVE = False
        stop_process(music_proc)
        servo_to_0()

def gen():
    global prev_gray, NUM_PLAYERS, PLAYER_NAMES, DETECTION_ACTIVE

    last_player = None
    last_time = 0

    kernel = np.ones((3, 3), np.uint8)

    last_detection_state = None

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, BLUR_SIZE, 0)

        if last_detection_state is None:
            last_detection_state = DETECTION_ACTIVE

        if DETECTION_ACTIVE != last_detection_state:
            prev_gray = gray
            last_detection_state = DETECTION_ACTIVE

        if prev_gray is None:
            prev_gray = gray
        else:
            delta = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(delta, PIXEL_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.erode(thresh, kernel, iterations=1)
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            prev_gray = gray

            h, w = thresh.shape
            zones = get_zones(w, NUM_PLAYERS)

            motion_counts = []
            for i, (x1, x2) in enumerate(zones):
                zone = thresh[:, x1:x2]
                motion_pixels = cv2.countNonZero(zone)
                motion_counts.append(motion_pixels)

            detected_player = None
            detected_idx = int(np.argmax(motion_counts)) if motion_counts else None
            max_motion = motion_counts[detected_idx] if detected_idx is not None else 0

            if DETECTION_ACTIVE and max_motion > ZONE_PIXEL_TRIGGER:
                detected_player = detected_idx + 1

            overlay = frame.copy()

            for i, (x1, x2) in enumerate(zones):
                pid = i + 1
                name = PLAYER_NAMES.get(pid, f"Joueur {pid}")

                cv2.rectangle(frame, (x1, 0), (x2, h), (80, 80, 80), 2)

                cv2.putText(frame, name, (x1 + 10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220, 220, 220), 2)

                if DETECTION_ACTIVE:
                    motion = motion_counts[i]
                    intensity = min(1.0, motion / float(ZONE_PIXEL_TRIGGER * 2))

                    if intensity > 0.05:
                        if detected_player == pid:
                            color = (0, 0, 255)
                            alpha = 0.35
                        else:
                            color = (0, 140, 255)
                            alpha = 0.15 * intensity

                        cv2.rectangle(overlay, (x1, 0), (x2, h), color, -1)
                        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            state_txt = "STOP (DETECTION ON)" if DETECTION_ACTIVE else "GO (DETECTION OFF)"
            cv2.putText(frame, state_txt, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (0, 0, 255) if DETECTION_ACTIVE else (0, 255, 0), 2)

            if detected_player:
                name = PLAYER_NAMES.get(detected_player, f"Joueur {detected_player}")
                cv2.putText(frame, f"{name} a bouge !", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

                now = time.time()
                if detected_player != last_player or now - last_time > COOLDOWN_SEC:
                    last_player = detected_player
                    last_time = now
                    eliminate_player(detected_player)

        ok, jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")

#ROUTES
@app.route("/")
def home():
    return redirect("/setup")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    global PLAYER_NAMES, NUM_PLAYERS, GAME_RUNNING

    if request.method == "POST":
        NUM_PLAYERS = int(request.form.get("nplayers", "4"))
        if NUM_PLAYERS not in (2, 3, 4):
            NUM_PLAYERS = 4

        for i in range(1, 5):
            name = request.form.get(f"p{i}", "").strip()
            PLAYER_NAMES[i] = name if name else f"Joueur {i}"

        return redirect("/view")

    options = "".join(
        f'<option value="{i}" {"selected" if i==NUM_PLAYERS else ""}>{i}</option>'
        for i in (2, 3, 4)
    )

    inputs = "".join(f"""
    <label>Joueur {i}</label>
    <input name="p{i}" value="{PLAYER_NAMES[i]}"
    style="width:100%;padding:10px;margin:6px 0;border-radius:8px;border:1px solid #444;background:#111;color:#eee;">
    """ for i in range(1, NUM_PLAYERS + 1))


    return f"""
    <html><body style="background:#111;color:#eee;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
    <form method="POST" style="background:#222;padding:20px;border-radius:12px;min-width:320px;">
        <h2>Setup joueurs</h2>

        <label>Nombre de joueurs</label>
        <select name="nplayers" style="width:100%;padding:10px;margin-bottom:10px;">
            {options}
        </select>

        {inputs}

        <button style="width:100%;padding:12px;margin-top:10px;
                background:#4CAF50;border:0;border-radius:10px;
                color:white;font-size:16px;">
            Démarrer
        </button>
    </form>
    </body></html>
    """

@app.route("/start")
def start():
    global GAME_RUNNING
    if not GAME_RUNNING:
        t = threading.Thread(target=game_loop, daemon=True)
        t.start()
    return redirect("/view")

@app.route("/stop")
def stop():
    global GAME_RUNNING
    GAME_RUNNING = False
    return redirect("/view")

@app.route("/stream")
def stream():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/view")
def view():
    return """
    <html><body style="margin:0;background:#111;display:flex;flex-direction:column;align-items:center;">
      <div style="padding:10px;color:#ddd;">
        <b>Caméra</b> —
        <a href="/setup" style="color:#7fd;">changer noms</a> |
        <a href="/start" style="color:#4CAF50;">START JEU</a> |
        <a href="/stop" style="color:#f55;">STOP</a>
      </div>
      <img src="/stream" style="width:95%;max-width:1100px;border:2px solid #333;border-radius:12px;">
    </body></html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, threaded=True)
