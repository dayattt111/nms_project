import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_alert(message):
    """Kirim alert sederhana ke Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Telegram alert sent: {message[:50]}...")
            return True
        else:
            print(f"❌ Failed to send Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending Telegram: {e}")
        return False


def send_device_down_alert(device_name, ip_address):
    """Alert untuk device down"""
    message = f"""
🚨 <b>DEVICE DOWN ALERT</b> 🚨

📌 Device: <b>{device_name}</b>
🌐 IP Address: <code>{ip_address}</code>
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

❌ Status: <b>DOWN</b>
⚠️ Device tidak dapat dijangkau!
"""
    return send_alert(message)


def send_device_up_alert(device_name, ip_address):
    """Alert untuk device up kembali"""
    message = f"""
✅ <b>DEVICE RECOVERED</b>

📌 Device: <b>{device_name}</b>
🌐 IP Address: <code>{ip_address}</code>
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Status: <b>UP</b>
🎉 Device sudah dapat dijangkau kembali!
"""
    return send_alert(message)


def send_bandwidth_alert(device_name, ip_address, bandwidth_data, threshold):
    """Alert untuk bandwidth tinggi"""
    in_mbps = bandwidth_data.get('in_mbps', 0)
    out_mbps = bandwidth_data.get('out_mbps', 0)
    total_mbps = bandwidth_data.get('total_mbps', 0)
    
    message = f"""
⚠️ <b>BANDWIDTH ALERT</b> ⚠️

📌 Device: <b>{device_name}</b>
🌐 IP Address: <code>{ip_address}</code>
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 <b>Bandwidth Usage:</b>
📥 Download: <b>{in_mbps} Mbps</b>
📤 Upload: <b>{out_mbps} Mbps</b>
📈 Total: <b>{total_mbps} Mbps</b>

🚨 Threshold: <b>{threshold} Mbps</b>
⚠️ Bandwidth usage melebihi threshold!
"""
    return send_alert(message)


def send_bandwidth_low_alert(device_name, ip_address, bandwidth_data, threshold):
    """Alert untuk bandwidth turun drastis"""
    in_mbps = bandwidth_data.get('in_mbps', 0)
    out_mbps = bandwidth_data.get('out_mbps', 0)
    total_mbps = bandwidth_data.get('total_mbps', 0)
    
    message = f"""
⬇️ <b>BANDWIDTH DROP ALERT</b> ⬇️

📌 Device: <b>{device_name}</b>
🌐 IP Address: <code>{ip_address}</code>
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 <b>Current Bandwidth:</b>
📥 Download: <b>{in_mbps} Mbps</b>
📤 Upload: <b>{out_mbps} Mbps</b>
📈 Total: <b>{total_mbps} Mbps</b>

📉 Minimum Threshold: <b>{threshold} Mbps</b>
⚠️ Bandwidth turun di bawah threshold minimum!
"""
    return send_alert(message)


def send_zabbix_trigger_alert(trigger_data):
    """Alert untuk Zabbix trigger"""
    severity_map = {
        0: "Not classified",
        1: "Information ℹ️",
        2: "Warning ⚠️",
        3: "Average 🟡",
        4: "High 🟠",
        5: "Disaster 🔴"
    }
    
    severity = severity_map.get(int(trigger_data.get('priority', 0)), "Unknown")
    description = trigger_data.get('description', 'N/A')
    host_name = trigger_data.get('hosts', [{}])[0].get('name', 'Unknown')
    
    message = f"""
🔔 <b>ZABBIX TRIGGER ALERT</b>

🖥️ Host: <b>{host_name}</b>
⚠️ Severity: <b>{severity}</b>
📋 Description: <b>{description}</b>
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔍 Check Zabbix dashboard untuk detail lebih lanjut.
"""
    return send_alert(message)


def send_monitoring_summary(summary_data):
    """Kirim ringkasan monitoring periodik"""
    total_devices = summary_data.get('total_devices', 0)
    up_devices = summary_data.get('up_devices', 0)
    down_devices = summary_data.get('down_devices', 0)
    avg_bandwidth = summary_data.get('avg_bandwidth', 0)
    
    message = f"""
📊 <b>MONITORING SUMMARY</b>

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 <b>Device Status:</b>
✅ Up: <b>{up_devices}</b>
❌ Down: <b>{down_devices}</b>
📦 Total: <b>{total_devices}</b>

🌐 <b>Network:</b>
📊 Avg Bandwidth: <b>{avg_bandwidth} Mbps</b>

{'✅ Semua sistem normal' if down_devices == 0 else '⚠️ Ada device yang down!'}
"""
    return send_alert(message)
