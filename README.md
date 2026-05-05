# 🛡️ Guardian Eye: Smart Panic SOS System

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-v3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Realtime_DB-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Guardian Eye** is a comprehensive emergency response network designed to provide real-time monitoring and rapid assistance during critical situations. Integrating **ESP32** hardware with a powerful cloud-based dashboard, it ensures that help is always just a button press away.

### 🆘 Core Emergency Logic
When the physical panic button is pressed:
1.  **Instant Alerts**: The system broadcasts live GPS coordinates to the dashboard.
2.  **Emergency SMS**: A text message containing the user's live **Google Maps location link** is sent to pre-configured emergency contacts.
3.  **Automatic Call**: The system initiates a direct voice call to the emergency responder for immediate communication.

---

## 🚀 Key Features

- **🔴 Real-Time Emergency Dashboard**: Instant notification and visual alerts when the panic button is triggered.
* **📍 Precision Live Tracking**: Real-time GPS location monitoring using Leaflet.js with historical path visualization.
* **🌦️ Smart Weather Monitor**: Automatically detects dangerous weather conditions (Thunderstorms, Heavy Rain, etc.) using the OpenWeather API and alerts users.
* **🔥 Firebase Integration**: Synchronized data across all devices with Firebase Realtime Database for near-zero latency.
* **📱 Responsive Design**: Modern, glassmorphic UI built with Tailwind CSS, optimized for both desktop and mobile viewing.
* **📊 Activation History**: Detailed logs of all emergency events, including timestamps and precise coordinates.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Microcontroller** | **ESP32** (Wi-Fi + Bluetooth) |
| **Communication** | **SIM7000 Module** (LTE/GPS/SMS/Call) |
| **Power Management** | **9V Battery** with **Buck Converter** |
| **Backend** | Python, Flask, Flask-SocketIO |
| **Database** | Firebase Realtime Database |
| **Frontend** | HTML5, Tailwind CSS, Lucide Icons |
| **Maps** | Leaflet.js (OpenStreetMap) |
| **Async Worker** | Eventlet |
| **APIs** | OpenWeatherMap API |

---

## 👥 The Team

We are a group of dedicated developers committed to building technology for safety and security.

- **Krishna Gupta**
- **Chitranshi Singh**
- **Aditya Pandey**
- **Kishan Kunar Shakya**
- **Yuvraj Jindal**
- **Devyansh Goyal**

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Kishan-Shakya/smart-panic-button-Iot.git
cd smart-panic-button-Iot
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and add your credentials:
```env
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
FIREBASE_DATABASE_URL=your_firebase_url
OPENWEATHER_API_KEY=your_api_key
FIREBASE_DATABASE_SECRET=your_secret
# ... and other Firebase Web Config variables
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Access the dashboard at `http://127.0.0.1:5000`

---

## 📜 Future Roadmap

- [ ] **Voice Feed Integration**: Live audio streaming from the device during emergencies.
- [ ] **SMS/Email Alerts**: Automated notifications to emergency contacts.
- [ ] **AI-Powered Danger Prediction**: Analyzing environmental data to predict risks.

---

*Project developed as part of the Emergency Response Network initiative.*
