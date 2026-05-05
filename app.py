from flask import Flask, render_template
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, db
import threading
import time
import requests
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# 🔐 Firebase Init
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ai-powered-road-accident-prev-default-rtdb.firebaseio.com'
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

API_KEY = "cf576e1857d97c5255874366a571faf5"
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
            print("⚠️ Location unavailable from Firebase. Using Mathura as default location.")
            lat = MATHURA_LAT
            lon = MATHURA_LON

        condition, description = get_weather(lat, lon)

        if condition:
            danger = is_dangerous(condition, description)

            print(f"[Weather] {condition} ({description}) | Danger: {danger}")

            if danger != last_danger_state:
                print("⚠️ Weather state changed → updating Firebase")
                update_firebase(condition, description, danger)
                last_danger_state = danger

        time.sleep(20)


# =========================
# 🌐 ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# 🚀 START THREADS
# =========================

def start_background_tasks():
    threading.Thread(target=realtime_dashboard, daemon=True).start()
    threading.Thread(target=weather_monitor, daemon=True).start()


if __name__ == "__main__":
    start_background_tasks()
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host="0.0.0.0", port=port)