import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, db
import threading
import time
import requests
import os
import socket
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# 🔐 Firebase Init
firebase_service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
firebase_database_url = os.getenv("FIREBASE_DATABASE_URL")
openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
firebase_database_secret = os.getenv("FIREBASE_DATABASE_SECRET")

firebase_web_config = {
    "apiKey": os.getenv("FIREBASE_WEB_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_WEB_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
}

if not firebase_service_account_path:
    raise ValueError("Missing FIREBASE_SERVICE_ACCOUNT_PATH in environment variables.")

if not firebase_database_url:
    raise ValueError("Missing FIREBASE_DATABASE_URL in environment variables.")

if not openweather_api_key:
    raise ValueError("Missing OPENWEATHER_API_KEY in environment variables.")

if not firebase_database_secret:
    raise ValueError("Missing FIREBASE_DATABASE_SECRET in environment variables.")

firebase_service_account_path = os.path.abspath(firebase_service_account_path)
if not os.path.exists(firebase_service_account_path):
    raise FileNotFoundError(
        f"Firebase service account file not found at: {firebase_service_account_path}. "
        "Set FIREBASE_SERVICE_ACCOUNT_PATH in .env to a valid local JSON key path."
    )

cred = credentials.Certificate(firebase_service_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_database_url
})

# =========================
# 🔴 REAL-TIME DASHBOARD
# =========================

last_sent = 0

def realtime_dashboard():
    global last_sent

    while True:
        ref = db.reference("panic_events")
        data = ref.get()

        if data:
            events = list(data.values())
            latest = max(events, key=lambda x: x.get("timestamp", 0))
            latest_ts = latest.get("timestamp", 0)

            if latest_ts > last_sent:
                last_sent = latest_ts
                socketio.emit("new_event", {
                    "events": events,
                    "latest": latest
                })

        time.sleep(3)


# =========================
# 🌦️ WEATHER MONITOR
# =========================

API_KEY = openweather_api_key
last_danger_state = None

# Mathura Fallback Coordinates
MATHURA_LAT = 27.60147256
MATHURA_LON = 77.59771284

def get_latest_location():
    ref = db.reference("panic_events")
    data = ref.get()

    if not data:
        return None, None

    events = list(data.values())
    latest = max(events, key=lambda x: x.get("timestamp", 0))

    return latest.get("latitude"), latest.get("longitude")


def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

    try:
        res = requests.get(url, timeout=5).json()
        condition = res["weather"][0]["main"]
        description = res["weather"][0]["description"]
        return condition, description
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None, None


def is_dangerous(condition, description):
    danger_main = ["Thunderstorm", "Tornado", "Squall", "Extreme"]

    if condition in danger_main:
        return True

    if description:
        desc = description.lower()
        if "heavy rain" in desc or "very heavy rain" in desc:
            return True

    return False


def update_firebase(condition, description, danger):
    ref = db.reference("alerts/weather")

    ref.set({
        "condition": condition,
        "description": description,
        "danger": danger,
        "timestamp": int(time.time())
    })


def weather_monitor():
    global last_danger_state

    while True:
        lat, lon = get_latest_location()

        # Fallback to Mathura if no location is available from Firebase
        if not lat or not lon:
            print("WARN: Location unavailable from Firebase. Using Mathura as default location.")
            lat = MATHURA_LAT
            lon = MATHURA_LON

        condition, description = get_weather(lat, lon)

        if condition:
            danger = is_dangerous(condition, description)

            print(f"[Weather] {condition} ({description}) | Danger: {danger}")

            if danger != last_danger_state:
                print("WARN: Weather state changed -> updating Firebase")
                update_firebase(condition, description, danger)
                last_danger_state = danger

        time.sleep(20)


# =========================
# 🌐 ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html", firebase_web_config=firebase_web_config)


# =========================
# 🚀 START THREADS
# =========================

def start_background_tasks():
    threading.Thread(target=realtime_dashboard, daemon=True).start()
    threading.Thread(target=weather_monitor, daemon=True).start()


def find_available_port(preferred_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex(("127.0.0.1", preferred_port)) != 0:
            return preferred_port

    # If preferred port is in use, ask OS for a free one.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


if __name__ == "__main__":
    start_background_tasks()
    preferred_port = int(os.environ.get("PORT", 5000))
    port = find_available_port(preferred_port)
    if port != preferred_port:
        print(f"WARN: Port {preferred_port} is busy. Using port {port} instead.")
    print(f"Dashboard Server starting on http://127.0.0.1:{port}")
    socketio.run(app, host="0.0.0.0", port=port)
