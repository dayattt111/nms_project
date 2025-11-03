from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from ping3 import ping
import mysql.connector
import os
from dotenv import load_dotenv
import requests

# --- Load Environment Variables (.env)
load_dotenv()

# --- Inisialisasi Flask
app = Flask(__name__)
CORS(app)  # Supaya bisa diakses dari frontend Vue

# --- Koneksi ke Database
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "nms_dcc")
    )
    return conn

# --- Fungsi kirim notifikasi ke Telegram
def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ Telegram token/chat_id belum diatur di .env")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
        print(f"✅ Notifikasi terkirim: {message}")
    except Exception as e:
        print(f"❌ Gagal kirim notifikasi Telegram: {e}")

# --- Fungsi untuk cek status perangkat
def check_devices():
    print(f"[{datetime.now()}] 🔍 Memeriksa perangkat...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()

    for device in devices:
        ip = device['ip_address']
        response = ping(ip, timeout=2)
        status = 'up' if response else 'down'

        cursor.execute("""
            UPDATE devices SET status=%s, last_checked=%s WHERE id=%s
        """, (status, datetime.now(), device['id']))
        conn.commit()

        # kirim alert kalau perangkat down
        if status == 'down':
            send_telegram_alert(f"⚠️ Perangkat {device['name']} ({ip}) tidak merespons!")

    cursor.close()
    conn.close()

# --- Route API utama
@app.route("/")
def home():
    return jsonify({"message": "NMS Flask API is running!"})

@app.route("/devices", methods=["GET"])
def get_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# --- Jalankan scheduler (cek otomatis setiap 60 detik)
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_devices, trigger="interval", seconds=60)
scheduler.start()

# --- Jalankan Flask
if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, port=5003)
