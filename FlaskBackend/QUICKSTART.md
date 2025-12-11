# Quick Start Guide - NMS System

## 🚀 Langkah Cepat Memulai

### 1️⃣ Persiapan Database

```bash
# Masuk ke MySQL
mysql -u root -p

# Import schema
mysql -u root -p < database_schema.sql

# Atau manual:
CREATE DATABASE nms_dcc;
USE nms_dcc;
source database_schema.sql;
```

### 2️⃣ Konfigurasi Environment

```bash
# Copy file .env.example ke .env
cp .env.example .env

# Edit .env dan sesuaikan dengan konfigurasi Anda
nano .env
```

**Konfigurasi Penting:**

```env
# Database - sesuaikan dengan MySQL Anda
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=nms_dcc

# SNMP Community String (biasanya 'public' atau 'private')
SNMP_COMMUNITY=public

# Telegram Bot
# 1. Chat dengan @BotFather di Telegram
# 2. Ketik /newbot dan ikuti instruksi
# 3. Copy token yang diberikan
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# 4. Chat dengan @userinfobot untuk mendapatkan chat ID Anda
TELEGRAM_CHAT_ID=123456789

# Zabbix (jika ada)
ZABBIX_URL=http://localhost/zabbix/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
```

### 3️⃣ Install Dependencies

```bash
# Pastikan Python 3.8+ terinstall
python --version

# Install requirements
pip install -r requirements.txt

# Atau menggunakan virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 4️⃣ Test Koneksi

```bash
# Test semua koneksi (database, SNMP, Telegram, Zabbix)
python test_connections.py
```

**Output yang diharapkan:**
```
✅ Database: PASSED
✅ Ping: PASSED
✅ SNMP: PASSED (jika ada device dengan SNMP)
✅ Telegram: PASSED
✅ Zabbix: PASSED (jika Zabbix terinstall)
```

### 5️⃣ Jalankan Aplikasi

```bash
# Development mode
python app.py

# Production mode (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Server akan berjalan di: **http://localhost:5000**

### 6️⃣ Test API

```bash
# Test endpoint utama
curl http://localhost:5000/

# List devices
curl http://localhost:5000/api/devices

# Tambah device baru
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Router Utama",
    "ip_address": "192.168.1.1",
    "device_type": "router",
    "location": "Data Center"
  }'

# Check bandwidth
curl http://localhost:5000/api/monitoring/bandwidth/1
```

## 📱 Setup Telegram Bot (Detail)

### Langkah 1: Buat Bot
1. Buka Telegram dan cari **@BotFather**
2. Ketik `/start`
3. Ketik `/newbot`
4. Masukkan nama bot: `NMS Monitor Bot`
5. Masukkan username bot: `nms_monitor_bot` (harus unik)
6. Copy **token** yang diberikan

### Langkah 2: Dapatkan Chat ID
1. Cari **@userinfobot** di Telegram
2. Ketik `/start`
3. Bot akan reply dengan info Anda, copy **ID**

### Langkah 3: Test Bot
```bash
# Ganti <TOKEN> dengan token bot Anda
curl https://api.telegram.org/bot<TOKEN>/getMe

# Test kirim pesan
curl -X POST https://api.telegram.org/bot<TOKEN>/sendMessage \
  -d "chat_id=<CHAT_ID>&text=Hello from NMS!"
```

## 🌐 Enable SNMP di Perangkat

### Router Cisco/Cisco-like
```
configure terminal
snmp-server community public RO
exit
write memory
```

### MikroTik
```
/snmp set enabled=yes
/snmp community add name=public address=0.0.0.0/0
```

### Linux Server
```bash
# Install SNMP daemon
sudo apt-get install snmpd

# Edit konfigurasi
sudo nano /etc/snmp/snmpd.conf

# Uncomment dan edit:
# rocommunity public 0.0.0.0/0

# Restart service
sudo systemctl restart snmpd
sudo systemctl enable snmpd
```

### Windows Server
```powershell
# Enable SNMP feature
Install-WindowsFeature -Name SNMP-Service
Get-Service SNMP | Start-Service
```

### Test SNMP
```bash
# Install snmp tools
sudo apt-get install snmp  # Linux
# atau
brew install net-snmp  # Mac

# Test SNMP
snmpwalk -v2c -c public 192.168.1.1 system
```

## 🔧 Troubleshooting

### Database Connection Error
```bash
# Cek MySQL running
sudo systemctl status mysql

# Test koneksi manual
mysql -u root -p -e "SELECT 1"

# Buat user baru jika perlu
mysql -u root -p
CREATE USER 'nms_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON nms_dcc.* TO 'nms_user'@'localhost';
FLUSH PRIVILEGES;
```

### SNMP Not Working
```bash
# Cek SNMP dari command line
snmpwalk -v2c -c public 192.168.1.1

# Cek firewall
sudo ufw allow 161/udp

# Verify SNMP service
sudo systemctl status snmpd
```

### Telegram Not Sending
```bash
# Verifikasi token valid
curl https://api.telegram.org/bot<TOKEN>/getMe

# Cek chat ID benar
curl https://api.telegram.org/bot<TOKEN>/getUpdates

# Test kirim manual
curl -X POST https://api.telegram.org/bot<TOKEN>/sendMessage \
  -d "chat_id=<CHAT_ID>&text=Test"
```

### Port Already in Use
```bash
# Cek port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill process atau gunakan port lain
kill -9 <PID>  # Linux/Mac

# Atau ubah port di app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📊 Monitoring Status

Setelah aplikasi berjalan, sistem akan otomatis:

- ✅ **Cek device status** setiap 60 detik
- 📊 **Monitor bandwidth** setiap 5 menit  
- 🔍 **Cek Zabbix triggers** setiap 2 menit
- 📋 **Kirim summary** setiap 6 jam

Anda akan menerima notifikasi Telegram untuk:
- 🚨 Device down/up
- ⚠️ Bandwidth tinggi
- 📉 Bandwidth turun drastis
- 🔔 Zabbix alerts

## 🎯 Next Steps

1. **Tambahkan device** via API atau database
2. **Sync dari Zabbix** jika tersedia: `POST /api/monitoring/sync-zabbix`
3. **Kustomisasi threshold** di database tabel `device_thresholds`
4. **Setup frontend** di folder VueFrontEnd
5. **Konfigurasi reverse proxy** (nginx/apache) untuk production

## 📞 Butuh Bantuan?

- Cek log error di console
- Jalankan `python test_connections.py`
- Review file `.env` configuration
- Cek documentation lengkap di `README.md`

---

**Selamat Monitoring! 🎉**
