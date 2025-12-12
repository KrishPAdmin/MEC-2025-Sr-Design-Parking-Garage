# Authors: Mohib Amin, Krish Patel

import os, json, threading, time, re, sys
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import serial


# setting up communication
if os.name == "nt":
    # Windows
    DEFAULT_SERIAL_PORT = "COM3"
else:
    if sys.platform == "darwin":
        # macOS
        DEFAULT_SERIAL_PORT = "/dev/cu.usbserial-110"
    else:
        # Linux fallback
        DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

SERIAL_PORT = os.environ.get("SERIAL_PORT", DEFAULT_SERIAL_PORT)
SERIAL_BAUD = int(os.environ.get("SERIAL_BAUD", "9600"))
SIMULATE = os.environ.get("SIMULATE", "0") == "1"

# figuring out the positions
SPOT_MAP = {
    2: ("L1", "D1E"),  # pin1:Level 1, Dollarama EV
    3: ("L1", "D1P"),  # pin2:Level 1, Dollarama Regular
    4: ("L1", "S1E"),  # pin17:Level 1, Sephora EV
    5: ("L1", "S1P"),  # pin18: Level 1, Sephora Regular
}

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# grab the source
@app.route("/")
def index():
    return render_template("index.html")

# live update
@app.route("/api/update", methods=["POST"])
def api_update():
    """Optional HTTP endpoint to update a spot manually."""
    data = request.get_json(silent=True) or {}
    level = data.get("level")
    spot = data.get("spot")
    occupied = bool(data.get("occupied"))
    if level not in ("L1", "L2") or not spot:
        return jsonify({"ok": False, "error": "bad payload"}), 400
    socketio.emit("spot_update", {"level": level, "spot": spot, "occupied": occupied})
    return jsonify({"ok": True})

# message to browser/lcl
def emit_update(level: str, spot: str, occupied: bool):
    socketio.emit("spot_update", {"level": level, "spot": spot, "occupied": occupied})


def parse_spot_line(line: str):
    # ignore line with no spot
    if "Spot" not in line:
        return []

    results = []
    # split at 'Spot ' but keep content after
    parts = line.split("Spot ")
    for part in parts[1:]:
        # part example: '2: 800 Empty\t'
        m = re.match(r"(\d+)\s*:\s*([0-9]+)\s*(Empty|Taken)", part)
        if not m:
            continue
        sensor_num = int(m.group(1))
        # value = int(m.group(2))  # you could use this if you want
        state_word = m.group(3)
        occupied = (state_word == "Taken")
        results.append((sensor_num, occupied))
    return results


def serial_loop():
    """listen to your Arduino text output and convert it into map updates."""
    ser = None
    while True:
        try:
            if ser is None:
                ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
                print(f"[serial] connected to {SERIAL_PORT} @ {SERIAL_BAUD}")
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            # debug print so you can see what your Arduino is sending
            print("[raw]", line)

            try:
                msg = json.loads(line)
                level = msg.get("level")
                spot = msg.get("spot")
                occupied = bool(msg.get("occupied"))
                if level in ("L1", "L2") and spot:
                    emit_update(level, spot, occupied)
                    continue
            except json.JSONDecodeError:
                pass

            for sensor_num, occupied in parse_spot_line(line):
                if sensor_num in SPOT_MAP:
                    level, spot = SPOT_MAP[sensor_num]
                    emit_update(level, spot, occupied)

        except Exception as e:
            print(f"[serial] error: {e}")
            try:
                if ser:
                    ser.close()
            except Exception:
                pass
            ser = None
            time.sleep(2)


def simulate_loop():
    """Demo mode: generate random updates if no Arduino is connected."""
    import random
    L1 = ["D1A","D1E","D1P","B1A","B1E","B1P","S1A","S1E","S1P","C1A","C1E","C1P","BIKEL","BIKER"]
    L2 = ["D2F","D2P","B2F","B2P1","B2P2","S2F","S2P","C2F","C2P1","C2P2"]
    allspots = [("L1", s) for s in L1] + [("L2", s) for s in L2]
    while True:
        level, spot = random.choice(allspots)
        occupied = random.choice([True, False, False])
        emit_update(level, spot, occupied)
        time.sleep(0.9)


if __name__ == "__main__":
    print(f"[config] SERIAL_PORT={SERIAL_PORT}, SERIAL_BAUD={SERIAL_BAUD}, SIMULATE={SIMULATE}")
    if SIMULATE:
        threading.Thread(target=simulate_loop, daemon=True).start()
    else:
        threading.Thread(target=serial_loop, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
