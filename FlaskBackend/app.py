from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from ping3 import ping
import mysql.connector
import os
from dotenv import load_dotenv
import requests
from pysnmp.hlapi import *

# --- Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# snmp
def get_snmp_value(ip, community, oid):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"SNMP error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"SNMP error: {errorStatus.prettyPrint()}")
            return None
        else:
            for varBind in varBinds:
                return int(varBind[1])
    except Exception as e:
        print(f"Error SNMP {ip}: {e}")
        return None

# --- Koneksi ke Database
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "nms_dcc")
    )
    return conn

# --- Kirim notifikasi Telegram
def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Telegram belum dikonfigurasi.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
        print(f"📢 Notifikasi terkirim: {message}")
    except Exception as e:
        print(f"❌ Gagal kirim Telegram: {e}")

# --- Cek status perangkat via ping
def check_devices():
    print(f"[{datetime.now()}] 🔍 Mengecek perangkat...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()

    for device in devices:
        ip = device['ip_address']
        response = ping(ip, timeout=2)
        status = 'up' if response else 'down'

        cursor.execute(
            "UPDATE devices SET status=%s, last_checked=%s WHERE id=%s",
            (status, datetime.now(), device['id'])
        )
        conn.commit()

        if status == 'down':
            send_telegram_alert(f"⚠️ Perangkat {device['name']} ({ip}) down!")

    cursor.close()
    conn.close()


# --- ROUTES (API) ------------------------------------------

@app.route("/")
def home():
    return jsonify({"message": "NMS Flask API running"})

# GET semua perangkat
@app.route("/devices", methods=["GET"])
def get_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# POST tambah perangkat baru
@app.route("/devices", methods=["POST"])
def add_device():
    data = request.json
    name = data.get("name")
    ip = data.get("ip_address")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO devices (name, ip_address, status, last_checked) VALUES (%s, %s, %s, %s)",
        (name, ip, "unknown", None)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Device added successfully"}), 201

# --- Ambil data SNMP (trafik jaringan)
from pysnmp.hlapi import *

def get_snmp_value(ip, community, oid):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"SNMP error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"SNMP error: {errorStatus.prettyPrint()}")
            return None
        else:
            for varBind in varBinds:
                return int(varBind[1])
    except Exception as e:
        print(f"Error SNMP {ip}: {e}")
        return None

@app.route("/traffic/<ip>", methods=["GET"])
def get_traffic(ip):
    community = os.getenv("SNMP_COMMUNITY", "public")

    # OID untuk interface pertama (bisa disesuaikan)
    oid_in = "1.3.6.1.2.1.2.2.1.10.1"  # ifInOctets
    oid_out = "1.3.6.1.2.1.2.2.1.16.1" # ifOutOctets

    in_bytes = get_snmp_value(ip, community, oid_in)
    out_bytes = get_snmp_value(ip, community, oid_out)

    if in_bytes is None or out_bytes is None:
        return jsonify({"error": "Gagal ambil data SNMP"}), 500

    # Konversi ke Mbps
    in_mbps = round((in_bytes * 8) / (1024*1024), 2)
    out_mbps = round((out_bytes * 8) / (1024*1024), 2)

    return jsonify({
        "ip": ip,
        "in_mbps": in_mbps,
        "out_mbps": out_mbps,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })



# PUT ubah perangkat
@app.route("/devices/<int:id>", methods=["PUT"])
def update_device(id):
    data = request.json
    name = data.get("name")
    ip = data.get("ip_address")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE devices SET name=%s, ip_address=%s WHERE id=%s",
        (name, ip, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Device updated successfully"})

# DELETE hapus perangkat
@app.route("/devices/<int:id>", methods=["DELETE"])
def delete_device(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devices WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Device deleted successfully"})

# --- Jalankan pengecekan otomatis
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_devices, trigger="interval", seconds=60)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
