# MEC-2025-Sr-Design-Parking-Garage
# Smart Parking Pathfinder (MKT Labs)

A real time parking occupancy and guidance demo that connects Arduino sensors to a live, browser based parking map.

## What this project does

- Reads parking spot sensors on an Arduino and classifies each spot as **Empty** or **Taken**
- Drives a WS2812 LED strip to visually indicate spot availability (green for free, red for occupied)
- Controls entrance and exit gate servos
- Streams live status over **Serial** to a **Flask + Socket.IO** server
- Updates a **two level** parking map UI in the browser in real time

## Architecture

Arduino (sensors, LEDs, servos)  
-> Serial (USB)  
-> Python backend (Flask + Flask-SocketIO)  
-> WebSocket events (spot_update)  
-> Browser UI (HTML + CSS + JS)

## Repo layout

Recommended structure (matches Flask conventions):

```text
.
├─ app.py
├─ requirements.txt
├─ Arduino/
│  └─ Arduino.ino
├─ templates/
│  └─ index.html
└─ static/
   ├─ app.js
   └─ style.css
```

If your files are currently in one folder, move `index.html` into `templates/` and move `app.js` and `style.css` into `static/`.

## Hardware overview (Arduino)

- Photoresistors connected to A0 to A5 (used for gate detection and parking spot detection)
- WS2812 LED strip on pin D5
- Entrance gate servo on pin D10
- Exit gate servo on pin D11
- Optional alarm or indicator on pin D8
- Optional fire sensor input on pin D9 (active low in the provided sketch)

The sketch prints lines like:

```text
Spot 2: 813 Empty    Spot 3: 145 Taken    ...
```

These lines are parsed by the Python backend and mapped to UI spot IDs.

## Backend (Python)

The server:
- Hosts the web UI at `/`
- Emits `spot_update` events over Socket.IO to update the UI instantly
- Can read either:
  - Plain text lines like `Spot 2: 800 Empty`
  - JSON lines like `{"level":"L1","spot":"D1E","occupied":true}`

### Configuration

Environment variables:

- `SERIAL_PORT` (default depends on OS)
- `SERIAL_BAUD` (default `9600`)
- `SIMULATE` set to `1` to run without an Arduino (random demo updates)
- `PORT` (default `5000`)

## Frontend (Web UI)

- Two level garage map with:
  - Store zones (Dollarama, Best Buy, Sephora, Canadian Tire)
  - Spot types: Accessibility, EV, Family, Bike
  - Tooltips on hover
  - Live counts and an availability bar per level

## Install and run

### 1) Create a virtual environment (recommended)

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the server

With Arduino connected:
```bash
python app.py
```

Demo mode without Arduino:
```bash
SIMULATE=1 python app.py
```

Then open:
- `http://localhost:5000`

## Manual update API (optional)

You can manually force a spot update via HTTP:

```bash
curl -X POST http://localhost:5000/api/update \
  -H "Content-Type: application/json" \
  -d '{"level":"L1","spot":"D1E","occupied":true}'
```

## Customization tips

- Add more hardware sensors by extending `SPOT_MAP` in `app.py`
- Change or add parking spots by editing:
  - The DOM elements in `templates/index.html`
  - The spot lists and counting logic in `static/app.js`
- Adjust visuals in `static/style.css`

## Troubleshooting

- **No live updates:** confirm the browser can reach the server and that Socket.IO is connected.
- **Serial errors:** set `SERIAL_PORT` explicitly to the correct device name, and verify the Arduino is using the same baud rate as `SERIAL_BAUD`.
- **Wrong spot updates:** update `SPOT_MAP` so Arduino sensor numbers map to the correct UI spot IDs.

## Credits

- Authors: Mohib Amin, Krish Patel, Muhammad Al-lami, Tom Croux
- Built as an MKT-Labs
