# Network Monitoring System (NMS)

🚀 **Sistem Monitoring Jaringan dengan Integrasi Zabbix dan Telegram**

Aplikasi monitoring jaringan yang powerful dengan kemampuan monitoring bandwidth real-time, integrasi Zabbix, dan notifikasi otomatis via Telegram.

---

## 📋 Deskripsi

Network Monitoring System (NMS) adalah aplikasi monitoring jaringan yang dirancang untuk:

- **Monitoring Real-time**: Pantau status perangkat dan bandwidth secara real-time menggunakan ICMP ping dan SNMP
- **Integrasi Zabbix**: Terhubung dengan Zabbix server untuk mengambil data monitoring yang lebih komprehensif
- **Notifikasi Telegram**: Dapatkan alert instant via Telegram ketika ada masalah pada jaringan
- **Bandwidth Monitoring**: Pantau penggunaan bandwidth dan dapatkan alert ketika threshold terlampaui
- **Dashboard Web**: Visualisasi data monitoring melalui interface web yang user-friendly

---

## ✨ Fitur Utama

### 🖥️ Device Management
- ✅ Tambah, edit, hapus perangkat monitoring
- ✅ Support berbagai tipe: Router, Switch, Server, Firewall
- ✅ Auto-discovery dari Zabbix
- ✅ Status monitoring (up/down)

### 📊 Bandwidth Monitoring
- 📈 Real-time bandwidth monitoring via SNMP
- 📉 Historical data & trending
- ⚠️ Alert bandwidth tinggi/rendah
- 🔄 Multi-interface support
- 💾 Data storage untuk analisis

### 🔔 Smart Alerts
- 🚨 Device down/up notifications
- 📊 Bandwidth threshold alerts
- 🔔 Zabbix trigger forwarding
- 📋 Periodic summary reports
- 🎨 Rich formatted messages

### 🔧 Zabbix Integration
- 🔗 Zabbix API integration
- 📥 Host synchronization
- 📊 Item & metric collection
- ⚠️ Trigger monitoring
- 🔄 Real-time data sync

### 🌐 Web Interface
- 🎨 Modern Vue.js frontend
- 📱 Responsive design
- 📊 Interactive charts
- 🔍 Real-time updates
- 🎯 User-friendly dashboard

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────┐
│                   Web Browser                       │
│              (Vue.js Frontend)                      │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────────┐
│              Flask Backend                          │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Routes (devices, monitoring, zabbix)    │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐  │
│  │           Services Layer                      │  │
│  │  • network_service.py (SNMP, Ping)           │  │
│  │  • zabbix_service.py (Zabbix API)            │  │
│  │  • telegram_service.py (Notifications)       │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐  │
│  │        Background Scheduler                   │  │
│  │  • Device status check (60s)                 │  │
│  │  • Bandwidth monitoring (5min)               │  │
│  │  • Zabbix triggers (2min)                    │  │
│  │  • Summary reports (6h)                      │  │
│  └──────────────────────────────────────────────┘  │
└──────────┬────────────────────┬────────────────────┘
           │                    │
           │                    └──────────────┐
           │                                   │
┌──────────▼──────────┐    ┌──────────────────▼──────┐
│   MySQL Database    │    │  External Services      │
│  • Devices          │    │  • Zabbix Server        │
│  • Bandwidth History│    │  • Telegram Bot API     │
│  • Alerts           │    │  • Network Devices      │
│  • Thresholds       │    │    (via SNMP)           │
└─────────────────────┘    └─────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.1.2
- **Database**: MySQL/MariaDB
- **Scheduler**: APScheduler
- **Networking**: ping3, pysnmp
- **APIs**: requests (REST API client)

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **UI**: Custom CSS with responsive design
- **Charts**: Chart.js / D3.js (optional)

### Integrations
- **Monitoring**: Zabbix API
- **Notifications**: Telegram Bot API
- **Protocol**: SNMP v2c/v3, ICMP

---

## 📦 Project Structure

```
nms_dcc/
├── README.md                    # This file
├── FlaskBackend/               # Backend application
│   ├── app.py                  # Main Flask application
│   ├── db.py                   # Database connection
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment configuration
│   ├── .env.example           # Example configuration
│   ├── database_schema.sql    # Database schema
│   ├── test_connections.py    # Connection tester
│   ├── README.md              # Backend documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── API_DOCUMENTATION.md   # API reference
│   ├── routes/                # API routes
│   │   ├── devices.py         # Device endpoints
│   │   └── monitoring.py      # Monitoring endpoints
│   └── service/               # Business logic
│       ├── network_service.py # Network monitoring
│       ├── telegram_service.py# Telegram notifications
│       └── zabbix_service.py  # Zabbix integration
│
└── VueFrontEnd/               # Frontend application
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.vue
        ├── main.js
        ├── components/
        ├── router/
        └── views/
```

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Python 3.8+
python --version

# Install MySQL/MariaDB
mysql --version

# Install Node.js & npm (untuk frontend)
node --version
npm --version
```

### 2. Backend Setup
```bash
cd FlaskBackend

# Install dependencies
pip install -r requirements.txt

# Setup database
mysql -u root -p < database_schema.sql

# Configure environment
cp .env.example .env
nano .env  # Edit dengan konfigurasi Anda

# Test connections
python test_connections.py

# Run application
python app.py
```

### 3. Frontend Setup
```bash
cd VueFrontEnd

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### 4. Access Application
- Backend API: http://localhost:5000
- Frontend: http://localhost:5173
- API Docs: http://localhost:5000/api

---

## 📖 Documentation

- **[Backend README](FlaskBackend/README.md)** - Dokumentasi lengkap backend
- **[Quick Start Guide](FlaskBackend/QUICKSTART.md)** - Panduan memulai cepat
- **[API Documentation](FlaskBackend/API_DOCUMENTATION.md)** - Referensi API lengkap

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=nms_dcc

# SNMP
SNMP_COMMUNITY=public

# Telegram
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Zabbix
ZABBIX_URL=http://localhost/zabbix/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix

# Thresholds
BANDWIDTH_THRESHOLD_HIGH=80
BANDWIDTH_THRESHOLD_LOW=1
```

---

## 📊 Monitoring Tasks

Sistem otomatis menjalankan task berikut:

| Task | Interval | Deskripsi |
|------|----------|-----------|
| Device Status Check | 60 detik | Cek status perangkat via ping |
| Bandwidth Monitoring | 5 menit | Monitor bandwidth via SNMP |
| Zabbix Trigger Check | 2 menit | Cek alert dari Zabbix |
| Summary Report | 6 jam | Kirim laporan summary |

---

## 🔔 Telegram Notifications

Notifikasi otomatis untuk:
- 🚨 Device down/up
- 📊 Bandwidth threshold exceeded
- 📉 Bandwidth drop detected
- ⚠️ Zabbix triggers
- 📋 Periodic summaries

---

## 🧪 Testing

### Test Backend
```bash
cd FlaskBackend

# Test all connections
python test_connections.py

# Test specific endpoint
curl http://localhost:5000/api/devices

# Test bandwidth monitoring
curl http://localhost:5000/api/monitoring/bandwidth/1
```

### Test SNMP
```bash
# Install snmp tools
sudo apt-get install snmp

# Test SNMP
snmpwalk -v2c -c public 192.168.1.1 system
```

---

## 🔐 Security Considerations

- ✅ Gunakan HTTPS di production
- ✅ Ubah default credentials
- ✅ Implementasi authentication
- ✅ Gunakan SNMP v3 untuk keamanan
- ✅ Batasi akses database
- ✅ Jangan commit file .env
- ✅ Update dependencies secara berkala

---

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Cek MySQL running
sudo systemctl status mysql

# Verifikasi credentials
mysql -u root -p
```

**SNMP Not Working**
```bash
# Test SNMP manual
snmpwalk -v2c -c public 192.168.1.1

# Cek firewall
sudo ufw allow 161/udp
```

**Telegram Not Sending**
```bash
# Verify bot token
curl https://api.telegram.org/bot<TOKEN>/getMe

# Test send message
curl -X POST https://api.telegram.org/bot<TOKEN>/sendMessage \
  -d "chat_id=<CHAT_ID>&text=Test"
```

---

## 🎯 Roadmap

- [ ] Authentication & Authorization
- [ ] Multi-user support
- [ ] Custom dashboard builder
- [ ] Historical data analytics
- [ ] Export reports (PDF/Excel)
- [ ] Mobile app
- [ ] NetFlow monitoring
- [ ] SLA tracking
- [ ] Multi-tenant support

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Team

Network Monitoring System Development Team

---

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/nms_dcc/issues)
- 📖 Docs: [Documentation](FlaskBackend/README.md)

---

## 🙏 Acknowledgments

- Flask Framework
- Vue.js Community
- Zabbix Project
- Telegram Bot API
- SNMP Community

---

**Happy Monitoring! 🚀📊**