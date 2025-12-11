# Network Monitoring System (NMS) - WiFi Focused

🚀 **Sistem Monitoring Jaringan dengan Fokus pada WiFi dan Bandwidth**

Aplikasi monitoring jaringan yang simple dan powerful untuk monitoring koneksi WiFi, bandwidth, dan status perangkat jaringan.

---

## 📋 Fitur Utama

### 🖥️ Device Monitoring
- ✅ Monitor status perangkat (up/down) via ICMP ping
- ✅ Support berbagai tipe: Router, Switch, WiFi AP, Server
- ✅ Auto-scan network untuk detect perangkat aktif
- ✅ Real-time status updates

### 📡 WiFi Monitoring
- 📱 Monitor jumlah client WiFi yang terhubung
- 📊 Tracking client count history
- ⚠️ Alert ketika client count turun drastis
- 📈 Signal strength monitoring (jika support)
- 🔄 Multi Access Point support

### 📊 Bandwidth Monitoring
- 📈 Real-time bandwidth monitoring via SNMP
- 📉 Traffic in/out per interface
- ⚠️ Alert bandwidth tinggi/rendah
- 💾 Historical data storage
- 🔄 Configurable thresholds

### 🔔 Telegram Notifications
- 🚨 Device down/up alerts
- 📊 Bandwidth threshold alerts
- 📡 WiFi client drop alerts
- 📋 Periodic summary reports
- 🎨 Rich formatted messages

### 📈 Dashboard & Analytics
- 📊 Real-time dashboard summary
- 📈 Bandwidth usage graphs
- 📡 WiFi client statistics
- 🕐 Historical data views
- 📋 Alert history

---

## 🛠️ Tech Stack

- **Backend**: Flask 3.1.2 + Python
- **Database**: MySQL/MariaDB
- **Monitoring**: SNMP v2c, ICMP Ping
- **Scheduler**: APScheduler
- **Notifications**: Telegram Bot API
- **Frontend**: Vue.js (optional)

---

## 📦 Installation

### 1. Clone & Setup
```bash
cd FlaskBackend

# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

### 2. Database Setup
```bash
mysql -u root -p < database_schema.sql
```

### 3. Configure .env
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=nms_dcc

# SNMP Community String
SNMP_COMMUNITY=public

# Telegram Bot
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Bandwidth Thresholds (Mbps)
BANDWIDTH_THRESHOLD_HIGH=80
BANDWIDTH_THRESHOLD_LOW=1

# WiFi Monitoring
WIFI_CLIENT_DROP_THRESHOLD=0.5
```

### 4. Test & Run
```bash
# Test connections
python test_connections.py

# Run application
python app.py
```

Server akan berjalan di: **http://localhost:5000**

---

## 📡 Enable SNMP di WiFi Access Point

### MikroTik
```
/snmp set enabled=yes
/snmp community add name=public address=0.0.0.0/0
```

### Ubiquiti UniFi
```
1. Login ke UniFi Controller
2. Settings → Services → SNMP
3. Enable SNMP
4. Set Community String: public
```

### TP-Link
```
1. Login web interface
2. System Tools → SNMP Settings
3. Enable SNMP Agent
4. Community: public
5. Save
```

### Cisco WLC (Wireless LAN Controller)
```
configure terminal
snmp-server community public RO
exit
write memory
```

---

## 📊 API Endpoints

### Device Management
```
GET    /api/devices                         - List all devices
GET    /api/devices?type=wifi_ap            - Filter by type
GET    /api/devices/<id>                    - Get device details
POST   /api/devices                         - Add new device
PUT    /api/devices/<id>                    - Update device
DELETE /api/devices/<id>                    - Delete device
```

### Bandwidth Monitoring
```
GET    /api/devices/<id>/bandwidth          - Get real-time bandwidth
GET    /api/devices/<id>/interfaces         - List device interfaces
GET    /api/bandwidth/history/<id>          - Get bandwidth history
```

### WiFi Monitoring
```
GET    /api/wifi/clients/<id>               - Get current WiFi clients
GET    /api/wifi/history/<id>               - Get client count history
```

### Network Tools
```
POST   /api/network/scan                    - Scan network for devices
GET    /api/dashboard/summary               - Get dashboard summary
```

---

## 🔧 Usage Examples

### 1. Tambah WiFi Access Point
```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WiFi AP Office",
    "ip_address": "192.168.1.2",
    "device_type": "wifi_ap",
    "location": "Office Floor 1",
    "vendor": "Ubiquiti",
    "model": "UAP-AC-PRO",
    "snmp_community": "public"
  }'
```

### 2. Monitor WiFi Clients
```bash
curl http://localhost:5000/api/wifi/clients/1
```

Response:
```json
{
  "success": true,
  "device": {
    "id": 1,
    "name": "WiFi AP Office",
    "ip_address": "192.168.1.2"
  },
  "client_count": 24,
  "timestamp": "2025-12-11T10:30:45"
}
```

### 3. Get Bandwidth
```bash
curl http://localhost:5000/api/devices/1/bandwidth
```

Response:
```json
{
  "success": true,
  "device": { ... },
  "bandwidth": {
    "in_mbps": 45.2,
    "out_mbps": 23.8,
    "total_mbps": 69.0,
    "timestamp": "2025-12-11T10:30:45"
  }
}
```

### 4. Scan Network
```bash
curl -X POST http://localhost:5000/api/network/scan \
  -H "Content-Type: application/json" \
  -d '{"network_range": "192.168.1.0/24"}'
```

### 5. Dashboard Summary
```bash
curl http://localhost:5000/api/dashboard/summary
```

Response:
```json
{
  "success": true,
  "summary": {
    "total_devices": 4,
    "up_devices": 3,
    "down_devices": 1,
    "total_wifi_clients": 42,
    "avg_bandwidth_mbps": 56.3,
    "recent_alerts": [...]
  }
}
```

---

## 📱 Telegram Notifications

### Device Down Alert
```
🚨 DEVICE DOWN ALERT 🚨

📌 Device: WiFi AP Office
🌐 IP Address: 192.168.1.2
⏰ Time: 2025-12-11 10:30:45

❌ Status: DOWN
⚠️ Device tidak dapat dijangkau!
```

### WiFi Client Alert
```
📡 WIFI CLIENT ALERT 📡

📌 Device: WiFi AP Office
🌐 IP Address: 192.168.1.2
⏰ Time: 2025-12-11 10:30:45

👥 Connected Clients:
📊 Current: 8 clients
📈 Average: 24 clients

⚠️ Client count dropped significantly!
🔍 Please check WiFi connectivity
```

### Bandwidth Alert
```
⚠️ BANDWIDTH ALERT ⚠️

📌 Device: Router Utama
🌐 IP Address: 192.168.1.1
⏰ Time: 2025-12-11 10:30:45

📊 Bandwidth Usage:
📥 Download: 85.5 Mbps
📤 Upload: 45.2 Mbps
📈 Total: 130.7 Mbps

🚨 Threshold: 80 Mbps
⚠️ Bandwidth usage melebihi threshold!
```

---

## ⚙️ Scheduled Tasks

Sistem otomatis menjalankan:

| Task | Interval | Fungsi |
|------|----------|--------|
| Device Status Check | 60 detik | Cek status via ping & alert |
| Bandwidth Monitoring | 5 menit | Monitor bandwidth & threshold |
| WiFi Client Monitoring | 3 menit | Monitor WiFi clients & alert |
| Summary Report | 6 jam | Kirim laporan ke Telegram |

---

## 📊 Monitoring WiFi

### Supported Vendors:
- ✅ MikroTik (RouterOS)
- ✅ Ubiquiti (UniFi)
- ✅ TP-Link
- ✅ Cisco (WLC)
- ✅ Generic SNMP-enabled APs

### SNMP OIDs Used:
```
# WiFi Client Count
MikroTik: 1.3.6.1.4.1.14988.1.1.1.3.1 (wireless registration table)
Cisco: 1.3.6.1.4.1.14179.2.1.1.1.38
Generic: 1.3.6.1.2.1.2.2.1.1 (interface count)

# Signal Strength
MikroTik: 1.3.6.1.4.1.14988.1.1.1.2.1.3

# Interface Traffic
ifInOctets: 1.3.6.1.2.1.2.2.1.10.{index}
ifOutOctets: 1.3.6.1.2.1.2.2.1.16.{index}
```

---

## 🔍 Troubleshooting

### SNMP Not Working
```bash
# Test SNMP manual
snmpwalk -v2c -c public 192.168.1.2

# Check firewall
sudo ufw allow 161/udp

# Verify SNMP enabled on device
```

### WiFi Client Count = 0
```
1. Verify SNMP enabled on AP
2. Check correct community string
3. Try different SNMP OID (vendor-specific)
4. Check AP supports client count via SNMP
```

### Telegram Not Sending
```bash
# Verify bot token
curl https://api.telegram.org/bot<TOKEN>/getMe

# Test send message
curl -X POST https://api.telegram.org/bot<TOKEN>/sendMessage \
  -d "chat_id=<CHAT_ID>&text=Test"
```

---

## 📝 Database Schema

```sql
devices
- id, name, ip_address
- device_type: router, switch, wifi_ap, server, firewall
- status, last_checked
- vendor, model, location

bandwidth_history
- device_id, timestamp
- in_mbps, out_mbps, total_mbps

wifi_client_history
- device_id, timestamp
- client_count, avg_signal_strength

alert_history
- device_id, alert_type
- severity, message, timestamp
```

---

## 🎯 Best Practices

1. **SNMP Community String**: Gunakan unique string, jangan "public" di production
2. **Monitoring Interval**: Adjust sesuai kebutuhan (default: 3-5 menit)
3. **Alert Threshold**: Set threshold sesuai kapasitas jaringan
4. **Data Retention**: Cleanup old data secara berkala
5. **Backup Database**: Regular backup untuk historical data

---

## 📞 Support

Untuk pertanyaan dan support:
- 📖 Dokumentasi: [README.md](README.md)
- 🐛 Issues: GitHub Issues
- 📧 Email: support@example.com

---

**Happy Monitoring! 🚀📡**
