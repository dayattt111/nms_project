# Network Monitoring System (NMS)

Aplikasi sistem monitoring jaringan berbasis Flask yang terintegrasi dengan Zabbix dan Telegram untuk monitoring bandwidth, status perangkat, dan alert real-time.

## 🚀 Fitur Utama

### 1. **Device Monitoring**
- ✅ Monitoring status perangkat (up/down) via ICMP ping
- ✅ Auto-discovery perangkat dari Zabbix
- ✅ Support berbagai tipe perangkat (router, switch, server, firewall)
- ✅ Tracking last check time

### 2. **Bandwidth Monitoring**
- 📊 Real-time bandwidth monitoring via SNMP
- 📈 Monitoring traffic in/out per interface
- 📉 Alert ketika bandwidth tinggi atau turun drastis
- 🔄 Periodic bandwidth checking
- 💾 History bandwidth untuk analisis

### 3. **Zabbix Integration**
- 🔗 Koneksi ke Zabbix API
- 📥 Sync host dari Zabbix ke database lokal
- 📊 Ambil data bandwidth dari Zabbix items
- ⚠️ Monitor Zabbix triggers/alerts
- 🔔 Forward Zabbix alerts ke Telegram

### 4. **Telegram Notifications**
- 🚨 Alert device down/up
- 📊 Alert bandwidth threshold (high/low)
- 📢 Zabbix trigger notifications
- 📋 Periodic monitoring summary
- 🎨 Formatted messages dengan HTML

### 5. **Scheduled Tasks**
- ⏰ Device status check: Every 60 seconds
- 📊 Bandwidth monitoring: Every 5 minutes
- 🔍 Zabbix trigger check: Every 2 minutes
- 📋 Summary report: Every 6 hours

## 📋 Prerequisites

- Python 3.8+
- MySQL/MariaDB
- Zabbix Server (optional, untuk integrasi Zabbix)
- SNMP enabled pada perangkat yang akan dimonitor
- Bot Telegram dan Chat ID

## 🛠️ Installation

### 1. Clone Repository
```bash
cd FlaskBackend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
mysql -u root -p < database_schema.sql
```

### 4. Konfigurasi Environment
Edit file `.env`:
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=nms_dcc

# SNMP
SNMP_COMMUNITY=public

# Telegram
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Zabbix
ZABBIX_URL=http://your-zabbix-server/zabbix/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=your_zabbix_password

# Bandwidth Thresholds (Mbps)
BANDWIDTH_THRESHOLD_HIGH=80
BANDWIDTH_THRESHOLD_LOW=1
```

### 5. Setup Telegram Bot
1. Buat bot baru di [@BotFather](https://t.me/botfather)
2. Dapatkan token dari BotFather
3. Dapatkan Chat ID dari [@userinfobot](https://t.me/userinfobot)
4. Masukkan ke `.env`

### 6. Enable SNMP di Perangkat
Untuk Router/Switch:
```
# Cisco
snmp-server community public RO

# MikroTik
/snmp set enabled=yes

# Linux
sudo apt-get install snmpd
sudo systemctl enable snmpd
```

## 🚀 Running Application

### Development Mode
```bash
python app.py
```

### Production Mode (dengan Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Server akan berjalan di `http://localhost:5000`

## 📡 API Endpoints

### Device Management
```
GET    /api/devices              - List semua device
POST   /api/devices              - Tambah device baru
PUT    /api/devices/<id>         - Update device
DELETE /api/devices/<id>         - Hapus device
```

### Monitoring
```
GET    /api/monitoring/bandwidth/<device_id>    - Get bandwidth device
GET    /api/monitoring/interfaces/<device_id>   - List interfaces device
GET    /api/monitoring/bandwidth/all            - Bandwidth semua device
POST   /api/monitoring/check-bandwidth          - Check threshold & alert
```

### Zabbix Integration
```
GET    /api/zabbix/hosts                        - List Zabbix hosts
GET    /api/zabbix/host/<hostid>/items          - Get host items
GET    /api/zabbix/host/<hostid>/bandwidth      - Get bandwidth dari Zabbix
GET    /api/zabbix/triggers                     - Get Zabbix triggers
POST   /api/zabbix/sync                         - Sync hosts dari Zabbix
```

## 📊 Usage Examples

### 1. Tambah Device Manual
```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Router Office",
    "ip_address": "192.168.1.1",
    "device_type": "router",
    "location": "Office Floor 1"
  }'
```

### 2. Check Bandwidth
```bash
curl http://localhost:5000/api/monitoring/bandwidth/1
```

### 3. Sync dari Zabbix
```bash
curl -X POST http://localhost:5000/api/monitoring/sync-zabbix
```

### 4. Get Zabbix Triggers
```bash
curl http://localhost:5000/api/zabbix/triggers?severity=3
```

## 🔧 Configuration

### SNMP OIDs
```python
# Traffic counters
ifInOctets  = 1.3.6.1.2.1.2.2.1.10.{interface_index}
ifOutOctets = 1.3.6.1.2.1.2.2.1.16.{interface_index}

# Interface info
ifDescr     = 1.3.6.1.2.1.2.2.1.2.{interface_index}
ifOperStatus= 1.3.6.1.2.1.2.2.1.8.{interface_index}
```

### Bandwidth Thresholds
Bisa dikonfigurasi per device di database atau global di `.env`:
- `BANDWIDTH_THRESHOLD_HIGH`: Alert jika bandwidth > nilai ini (Mbps)
- `BANDWIDTH_THRESHOLD_LOW`: Alert jika bandwidth < nilai ini (Mbps)

### Scheduler Intervals
Edit di `app.py`:
```python
scheduler.add_job(func=check_devices_with_alert, trigger="interval", seconds=60)
scheduler.add_job(func=monitor_bandwidth, trigger="interval", minutes=5)
scheduler.add_job(func=check_zabbix_triggers, trigger="interval", minutes=2)
scheduler.add_job(func=send_periodic_summary, trigger="interval", hours=6)
```

## 📁 Project Structure

```
FlaskBackend/
├── app.py                      # Main application
├── db.py                       # Database connection
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── database_schema.sql         # Database schema
├── routes/
│   ├── devices.py             # Device management endpoints
│   └── monitoring.py          # Monitoring & Zabbix endpoints
└── service/
    ├── network_service.py     # Network monitoring functions
    ├── telegram_service.py    # Telegram notification functions
    └── zabbix_service.py      # Zabbix API integration
```

## 🔍 Troubleshooting

### SNMP Error
- Pastikan SNMP enabled di perangkat
- Cek community string yang benar
- Test dengan snmpwalk: `snmpwalk -v2c -c public 192.168.1.1`

### Telegram Not Sending
- Verifikasi token dan chat ID
- Cek koneksi internet
- Test manual: `curl https://api.telegram.org/bot<TOKEN>/getMe`

### Zabbix Connection Failed
- Cek URL Zabbix API
- Verifikasi username/password
- Pastikan Zabbix API enabled

### Database Connection
- Cek MySQL service running
- Verifikasi credentials di `.env`
- Import database schema

## 📈 Monitoring Dashboard

Untuk dashboard frontend, Anda bisa menggunakan:
- Vue.js frontend (sudah ada di VueFrontEnd/)
- Grafana untuk visualisasi
- Zabbix built-in dashboard

## 🔐 Security Notes

1. **Ubah default credentials** di `.env`
2. **Gunakan HTTPS** di production
3. **Batasi akses API** dengan authentication
4. **Gunakan SNMP v3** untuk security lebih baik
5. **Jangan commit** file `.env` ke git

## 📝 TODO / Future Improvements

- [ ] Authentication & authorization
- [ ] WebSocket untuk real-time updates
- [ ] Historical graphs & analytics
- [ ] Multi-user support dengan role management
- [ ] Export reports (PDF, Excel)
- [ ] Custom alert rules
- [ ] SNMP v3 support
- [ ] NetFlow monitoring
- [ ] SLA tracking
- [ ] Mobile app

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 👥 Author

Network Monitoring System Team

## 📞 Support

Untuk pertanyaan dan support, silakan buat issue di repository atau hubungi tim development.

---

**Happy Monitoring! 🚀📊**
