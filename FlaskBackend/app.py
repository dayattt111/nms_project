from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from ping3 import ping
import mysql.connector
import os
from dotenv import load_dotenv
import requests
from pysnmp.hlapi import *
import time

# Import routes
from routes.devices import devices_bp

# Import services
from service.network_service import check_devices, get_interface_bandwidth, get_wifi_clients
from service.telegram_service import (
    send_device_down_alert, 
    send_device_up_alert,
    send_bandwidth_alert,
    send_monitoring_summary,
    send_wifi_client_alert
)

# --- Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(devices_bp, url_prefix='/api')

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


# --- Poll data from HTTP API (for fake routers)
def poll_device_http_api(device):
    """Poll device data from HTTP API if available"""
    try:
        http_port = device.get('http_port', 8080)
        ip = device['ip_address']
        
        # Try to get WiFi info
        wifi_url = f"http://{ip}:{http_port}/wifi"
        response = requests.get(wifi_url, timeout=5)
        
        if response.status_code == 200:
            wifi_data = response.json()
            return wifi_data
    except Exception as e:
        pass
    
    return None


# --- Monitoring bandwidth untuk semua device
def monitor_bandwidth():
    print(f"[{datetime.now()}] 📊 Monitoring bandwidth...")
    
    threshold_high = float(os.getenv('BANDWIDTH_THRESHOLD_HIGH', 80))  # Mbps
    threshold_low = float(os.getenv('BANDWIDTH_THRESHOLD_LOW', 1))     # Mbps
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices WHERE status='up'")
    devices = cursor.fetchall()
    
    community = os.getenv('SNMP_COMMUNITY', 'public')
    
    for device in devices:
        try:
            bandwidth_data = None
            
            # Try HTTP API first (for fake routers)
            http_data = poll_device_http_api(device)
            if http_data and 'bandwidth_usage' in http_data:
                bandwidth_data = {
                    'in_mbps': http_data['bandwidth_usage'].get('download_mbps', 0),
                    'out_mbps': http_data['bandwidth_usage'].get('upload_mbps', 0),
                    'total_mbps': http_data['bandwidth_usage'].get('total_mbps', 0),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store WiFi client count if available
                if 'connected_clients' in http_data:
                    cursor.execute("""
                        INSERT INTO wifi_client_history (device_id, client_count, timestamp)
                        VALUES (%s, %s, %s)
                    """, (device['id'], http_data['connected_clients'], datetime.now()))
                
                print(f"📊 {device['name']}: {bandwidth_data['total_mbps']} Mbps (HTTP API)")
            
            # Fallback to SNMP
            if not bandwidth_data:
                bandwidth_data = get_interface_bandwidth(device['ip_address'], community)
                if bandwidth_data:
                    print(f"📊 {device['name']}: {bandwidth_data['total_mbps']} Mbps (SNMP)")
            
            if bandwidth_data:
                total_mbps = bandwidth_data.get('total_mbps', 0)
                
                # Store bandwidth history
                cursor.execute("""
                    INSERT INTO bandwidth_history 
                    (device_id, in_mbps, out_mbps, total_mbps, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    device['id'],
                    bandwidth_data.get('in_mbps', 0),
                    bandwidth_data.get('out_mbps', 0),
                    total_mbps,
                    datetime.now()
                ))
                
                # Check thresholds
                if total_mbps > threshold_high:
                    send_bandwidth_alert(
                        device['name'],
                        device['ip_address'],
                        bandwidth_data,
                        threshold_high
                    )
                elif total_mbps < threshold_low and total_mbps > 0:
                    print(f"⚠️ Low bandwidth detected on {device['name']}: {total_mbps} Mbps")
        except Exception as e:
            print(f"❌ Error monitoring {device['name']}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()


# --- Monitor WiFi clients
def monitor_wifi_clients():
    print(f"[{datetime.now()}] 📡 Monitoring WiFi clients...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE device_type='wifi_ap' AND status='up'")
        wifi_devices = cursor.fetchall()
        
        community = os.getenv('SNMP_COMMUNITY', 'public')
        
        for device in wifi_devices:
            try:
                # Get WiFi client count
                clients = get_wifi_clients(device['ip_address'], community)
                
                if clients is not None:
                    # Store client count
                    cursor.execute("""
                        INSERT INTO wifi_client_history (device_id, client_count, timestamp)
                        VALUES (%s, %s, %s)
                    """, (device['id'], clients, datetime.now()))
                    conn.commit()
                    
                    # Check if client count dropped significantly
                    cursor.execute("""
                        SELECT client_count FROM wifi_client_history
                        WHERE device_id=%s AND timestamp > %s
                        ORDER BY timestamp DESC LIMIT 5
                    """, (device['id'], datetime.now() - timedelta(minutes=30)))
                    
                    history = cursor.fetchall()
                    if len(history) > 1:
                        avg_clients = sum(h['client_count'] for h in history) / len(history)
                        if clients < avg_clients * 0.5:  # Drop 50%
                            send_wifi_client_alert(
                                device['name'],
                                device['ip_address'],
                                clients,
                                int(avg_clients)
                            )
                    
                    print(f"📡 {device['name']}: {clients} clients connected")
                    
            except Exception as e:
                print(f"❌ Error monitoring WiFi on {device['name']}: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in WiFi monitoring: {e}")


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

# --- WiFi Monitoring Routes
@app.route("/api/wifi/clients/<int:device_id>", methods=["GET"])
def get_wifi_clients_api(device_id):
    """Get current WiFi clients for an Access Point"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE id=%s AND device_type='wifi_ap'", (device_id,))
        device = cursor.fetchone()
        
        if not device:
            return jsonify({"error": "WiFi AP not found"}), 404
        
        community = os.getenv('SNMP_COMMUNITY', 'public')
        clients = get_wifi_clients(device['ip_address'], community)
        
        cursor.close()
        conn.close()
        
        if clients is not None:
            return jsonify({
                "success": True,
                "device": device,
                "client_count": clients,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Could not retrieve WiFi client data"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wifi/history/<int:device_id>", methods=["GET"])
def get_wifi_history(device_id):
    """Get WiFi client history for past 24 hours"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM wifi_client_history
            WHERE device_id=%s AND timestamp > %s
            ORDER BY timestamp DESC
        """, (device_id, datetime.now() - timedelta(hours=hours)))
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "device_id": device_id,
            "count": len(history),
            "history": history
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bandwidth/history/<int:device_id>", methods=["GET"])
def get_bandwidth_history(device_id):
    """Get bandwidth history for device"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM bandwidth_history
            WHERE device_id=%s AND timestamp > %s
            ORDER BY timestamp DESC
        """, (device_id, datetime.now() - timedelta(hours=hours)))
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "device_id": device_id,
            "count": len(history),
            "history": history
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    """Get dashboard summary data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get device stats
        cursor.execute("SELECT COUNT(*) as total FROM devices")
        total_devices = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as up FROM devices WHERE status='up'")
        up_devices = cursor.fetchone()['up']
        
        # Get WiFi clients
        cursor.execute("""
            SELECT SUM(wch.client_count) as total_clients
            FROM (
                SELECT device_id, MAX(timestamp) as max_time
                FROM wifi_client_history
                WHERE timestamp > %s
                GROUP BY device_id
            ) latest
            JOIN wifi_client_history wch ON wch.device_id = latest.device_id 
                AND wch.timestamp = latest.max_time
        """, (datetime.now() - timedelta(minutes=10),))
        
        wifi_result = cursor.fetchone()
        total_wifi_clients = wifi_result['total_clients'] if wifi_result['total_clients'] else 0
        
        # Get recent alerts
        cursor.execute("""
            SELECT * FROM alert_history
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_alerts = cursor.fetchall()
        
        # Get average bandwidth
        cursor.execute("""
            SELECT AVG(total_mbps) as avg_bandwidth
            FROM bandwidth_history
            WHERE timestamp > %s
        """, (datetime.now() - timedelta(hours=1),))
        
        bw_result = cursor.fetchone()
        avg_bandwidth = round(bw_result['avg_bandwidth'], 2) if bw_result['avg_bandwidth'] else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "summary": {
                "total_devices": total_devices,
                "up_devices": up_devices,
                "down_devices": total_devices - up_devices,
                "total_wifi_clients": int(total_wifi_clients),
                "avg_bandwidth_mbps": avg_bandwidth,
                "recent_alerts": recent_alerts
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Jalankan pengecekan otomatis
scheduler = BackgroundScheduler()

# Check device status every 1 minute
scheduler.add_job(func=check_devices_with_alert, trigger="interval", seconds=60)

# Monitor bandwidth every 5 minutes
scheduler.add_job(func=monitor_bandwidth, trigger="interval", minutes=5)

# Monitor WiFi clients every 3 minutes
scheduler.add_job(func=monitor_wifi_clients, trigger="interval", minutes=3)

# Send summary every 6 hours
scheduler.add_job(func=send_periodic_summary, trigger="interval", hours=6)

scheduler.start()

print("✅ NMS System started successfully!")
print("📊 Scheduled tasks:")
print("  - Device status check: Every 60 seconds")
print("  - Bandwidth monitoring: Every 5 minutes")
print("  - WiFi client monitoring: Every 3 minutes")
print("  - Summary report: Every 6 hours")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
