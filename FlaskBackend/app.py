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

# Import routes
from routes.devices import devices_bp
from routes.monitoring import monitoring_bp

# Import services
from service.network_service import check_devices, get_interface_bandwidth
from service.telegram_service import (
    send_device_down_alert, 
    send_device_up_alert,
    send_bandwidth_alert,
    send_monitoring_summary
)
from service.zabbix_service import ZabbixAPI

# --- Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(devices_bp, url_prefix='/api')
app.register_blueprint(monitoring_bp, url_prefix='/api')

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

# --- Cek status perangkat via ping dengan alert yang lebih baik
def check_devices_with_alert():
    print(f"[{datetime.now()}] 🔍 Mengecek perangkat...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()

    for device in devices:
        ip = device['ip_address']
        old_status = device['status']
        response = ping(ip, timeout=2)
        new_status = 'up' if response else 'down'

        cursor.execute(
            "UPDATE devices SET status=%s, last_checked=%s WHERE id=%s",
            (new_status, datetime.now(), device['id'])
        )
        conn.commit()

        # Send alert only on status change
        if old_status == 'up' and new_status == 'down':
            send_device_down_alert(device['name'], ip)
        elif old_status == 'down' and new_status == 'up':
            send_device_up_alert(device['name'], ip)

    cursor.close()
    conn.close()


# --- Monitoring bandwidth untuk semua device
def monitor_bandwidth():
    print(f"[{datetime.now()}] 📊 Monitoring bandwidth...")
    
    threshold_high = float(os.getenv('BANDWIDTH_THRESHOLD_HIGH', 80))  # Mbps
    threshold_low = float(os.getenv('BANDWIDTH_THRESHOLD_LOW', 1))     # Mbps
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices WHERE status='up'")
    devices = cursor.fetchall()
    cursor.close()
    conn.close()
    
    community = os.getenv('SNMP_COMMUNITY', 'public')
    
    for device in devices:
        try:
            bandwidth_data = get_interface_bandwidth(device['ip_address'], community)
            
            if bandwidth_data:
                total_mbps = bandwidth_data.get('total_mbps', 0)
                
                # Check thresholds
                if total_mbps > threshold_high:
                    send_bandwidth_alert(
                        device['name'],
                        device['ip_address'],
                        bandwidth_data,
                        threshold_high
                    )
                elif total_mbps < threshold_low and total_mbps > 0:
                    # Bandwidth too low might indicate problem
                    print(f"⚠️ Low bandwidth detected on {device['name']}: {total_mbps} Mbps")
        except Exception as e:
            print(f"❌ Error monitoring {device['name']}: {e}")


# --- Check Zabbix triggers
def check_zabbix_triggers():
    print(f"[{datetime.now()}] 🔍 Checking Zabbix triggers...")
    
    try:
        from service.telegram_service import send_zabbix_trigger_alert
        zabbix = ZabbixAPI()
        
        if zabbix.authenticate():
            triggers = zabbix.get_triggers(min_severity=3)  # High and above
            
            for trigger in triggers:
                # You might want to store trigger IDs to avoid duplicate alerts
                print(f"⚠️ Zabbix trigger: {trigger.get('description')}")
                send_zabbix_trigger_alert(trigger)
    except Exception as e:
        print(f"❌ Error checking Zabbix triggers: {e}")


# --- Send periodic summary
def send_periodic_summary():
    print(f"[{datetime.now()}] 📊 Sending monitoring summary...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM devices")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as up FROM devices WHERE status='up'")
        up = cursor.fetchone()['up']
        
        cursor.close()
        conn.close()
        
        summary = {
            'total_devices': total,
            'up_devices': up,
            'down_devices': total - up,
            'avg_bandwidth': 0  # Could calculate average if storing data
        }
        
        send_monitoring_summary(summary)
    except Exception as e:
        print(f"❌ Error sending summary: {e}")


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

# Check device status every 1 minute
scheduler.add_job(func=check_devices_with_alert, trigger="interval", seconds=60)

# Monitor bandwidth every 5 minutes
scheduler.add_job(func=monitor_bandwidth, trigger="interval", minutes=5)

# Check Zabbix triggers every 2 minutes
scheduler.add_job(func=check_zabbix_triggers, trigger="interval", minutes=2)

# Send summary every 6 hours
scheduler.add_job(func=send_periodic_summary, trigger="interval", hours=6)

scheduler.start()

print("✅ NMS System started successfully!")
print("📊 Scheduled tasks:")
print("  - Device status check: Every 60 seconds")
print("  - Bandwidth monitoring: Every 5 minutes")
print("  - Zabbix trigger check: Every 2 minutes")
print("  - Summary report: Every 6 hours")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
