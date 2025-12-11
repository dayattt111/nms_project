# 🧪 Fake Router/Server Simulator - Documentation

## Overview

Fake router simulator untuk testing aplikasi NMS tanpa memerlukan hardware fisik. Simulator ini menyediakan:
- HTTP API untuk monitoring
- Simulasi WiFi dengan data bandwidth
- Multiple routers dengan karakteristik berbeda
- Variasi kondisi jaringan (normal, high traffic, low signal, dll)

---

## 📁 File Simulator

### 1. `fake_router.py`
Single fake router pada port 8080

### 2. `fake_multiple_routers.py` ⭐ **Recommended**
Multiple fake routers dengan konfigurasi berbeda

---

## 🚀 Cara Menggunakan

### Opsi 1: Single Router

```bash
cd FlaskBackend
python fake_router.py
```

Router akan berjalan di: `http://localhost:8080`

### Opsi 2: Multiple Routers (Recommended)

```bash
cd FlaskBackend
python fake_multiple_routers.py
```

Routers yang akan dibuat:
- **Router-Office-1**: http://localhost:8081
- **Router-Office-2**: http://localhost:8082  
- **AP-Meeting-Room**: http://localhost:8083

---

## 📡 Available Endpoints

Setiap fake router memiliki endpoints berikut:

### 1. Home Page
```
GET http://localhost:8081/
```
Web interface dengan informasi router

### 2. Device Status
```
GET http://localhost:8081/status
```

**Response:**
```json
{
  "device": "Router-Office-1",
  "location": "Lantai 1",
  "device_type": "router",
  "status": "online",
  "uptime_seconds": 3600,
  "cpu_usage": 45,
  "memory_usage": 60,
  "temperature": 48,
  "interfaces": {
    "eth0": {
      "name": "WAN",
      "status": "up",
      "speed": "1000Mbps",
      "rx_bytes": 12345678,
      "tx_bytes": 6789012
    },
    "wlan0": {
      "name": "WiFi 2.4GHz",
      "status": "up",
      "speed": "300Mbps",
      "signal": -45,
      "noise": -85
    }
  }
}
```

### 3. WiFi Information
```
GET http://localhost:8081/wifi
```

**Response:**
```json
{
  "ssid": "Office-WiFi-1",
  "device": "Router-Office-1",
  "location": "Lantai 1",
  "channel": 6,
  "frequency": "2.4GHz",
  "connected_clients": 8,
  "signal_strength": -45,
  "bandwidth_usage": {
    "download_mbps": 42.5,
    "upload_mbps": 12.8,
    "total_mbps": 55.3
  },
  "security": "WPA2-PSK",
  "quality": "good"
}
```

### 4. Device Info
```
GET http://localhost:8081/api/info
```

**Response:**
```json
{
  "device_name": "Router-Office-1",
  "model": "Fake Router v1.0",
  "location": "Lantai 1",
  "ip_address": "127.0.0.1",
  "port": 8081,
  "ssid": "Office-WiFi-1",
  "firmware_version": "1.0.0",
  "mac_address": "00:11:22:33:81:00",
  "capabilities": ["wifi", "ethernet", "http_api", "ping"]
}
```

---

## 🔧 Integrasi dengan NMS

### Step 1: Start Fake Routers

```bash
# Terminal 1: Start fake routers
python fake_multiple_routers.py
```

### Step 2: Start NMS Application

```bash
# Terminal 2: Start NMS
python app.py
```

### Step 3: Add Devices ke NMS

#### Via cURL:

```bash
# Add Router-Office-1
curl -X POST http://localhost:5000/api/devices \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Router-Office-1",
    "ip_address": "127.0.0.1",
    "device_type": "router",
    "location": "Lantai 1",
    "http_port": 8081
  }'

# Add Router-Office-2
curl -X POST http://localhost:5000/api/devices \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Router-Office-2",
    "ip_address": "127.0.0.1",
    "device_type": "router",
    "location": "Lantai 2",
    "http_port": 8082
  }'

# Add AP-Meeting-Room
curl -X POST http://localhost:5000/api/devices \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "AP-Meeting-Room",
    "ip_address": "127.0.0.1",
    "device_type": "wifi_ap",
    "location": "Meeting Room",
    "http_port": 8083
  }'
```

#### Via MySQL:

```sql
INSERT INTO devices (name, ip_address, device_type, location, http_port) VALUES
('Router-Office-1', '127.0.0.1', 'router', 'Lantai 1', 8081),
('Router-Office-2', '127.0.0.1', 'router', 'Lantai 2', 8082),
('AP-Meeting-Room', '127.0.0.1', 'wifi_ap', 'Meeting Room', 8083);
```

---

## 🧪 Testing

### Test Individual Router

```bash
# Get status
curl http://localhost:8081/status

# Get WiFi info
curl http://localhost:8081/wifi

# Get device info
curl http://localhost:8081/api/info
```

### Test dari NMS

```bash
# Get all devices
curl http://localhost:5000/api/devices

# Get bandwidth for device ID 1
curl http://localhost:5000/api/devices/1/bandwidth

# Get WiFi info for device ID 1
curl http://localhost:5000/api/devices/1/wifi
```

---

## 📊 Karakteristik Fake Routers

### Router-Office-1
- **Port**: 8081
- **SSID**: Office-WiFi-1
- **Base Bandwidth**: 50 Mbps
- **Reliability**: 95% (jarang down)
- **Location**: Lantai 1

### Router-Office-2
- **Port**: 8082
- **SSID**: Office-WiFi-2
- **Base Bandwidth**: 30 Mbps
- **Reliability**: 90% (kadang degraded)
- **Location**: Lantai 2

### AP-Meeting-Room
- **Port**: 8083
- **SSID**: Meeting-WiFi
- **Base Bandwidth**: 20 Mbps
- **Reliability**: 85% (lebih sering masalah)
- **Location**: Meeting Room

---

## 🎭 Simulasi Kondisi

Fake routers akan secara random mensimulasikan:

### Normal Operation
- Bandwidth stabil
- CPU usage 10-80%
- Semua interface UP
- Signal strength bagus (-30 hingga -70 dBm)

### High Traffic
- Bandwidth usage tinggi (80-120% dari base)
- CPU usage meningkat
- Banyak clients connected

### Low Signal
- Signal strength lemah (-70 hingga -85 dBm)
- Bandwidth menurun
- Packet errors meningkat

### Degraded
- Status "degraded"
- Interface errors
- Client count menurun drastis
- Bandwidth sangat rendah

---

## 🔍 Monitoring yang Tersedia

NMS akan otomatis monitor:

1. **Device Status** (60 detik)
   - Ping test
   - Up/Down detection
   - Alert via Telegram

2. **Bandwidth Usage** (5 menit)
   - Download/Upload speed
   - Total bandwidth
   - Threshold alerts

3. **WiFi Clients** (5 menit)
   - Connected clients count
   - Client drop detection
   - Signal strength

4. **Device Health** (5 menit)
   - CPU usage
   - Memory usage
   - Temperature
   - Interface status

---

## 💡 Tips

### Custom Configuration

Edit `fake_multiple_routers.py` untuk menambah router:

```python
router_configs.append({
    'name': 'Router-Custom',
    'port': 8084,
    'ip': '127.0.0.1',
    'ssid': 'Custom-WiFi',
    'location': 'Custom Location',
    'device_type': 'router',
    'base_bandwidth': 100,
    'reliability': 0.98
})
```

### Simulate Device Down

Stop fake router dengan Ctrl+C, NMS akan detect device down dan kirim alert.

### Simulate High Bandwidth

Fake router secara random akan generate high bandwidth. Atau edit `base_bandwidth` di config untuk nilai lebih tinggi.

### Test Alert System

1. Set threshold rendah di `.env`:
   ```env
   BANDWIDTH_THRESHOLD_HIGH=5
   ```

2. Restart NMS:
   ```bash
   python app.py
   ```

3. Tunggu monitoring cycle, alert akan masuk ke Telegram

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Cek port yang digunakan
netstat -ano | findstr :8081

# Ubah port di fake_multiple_routers.py
'port': 8091  # Ganti ke port lain
```

### NMS Tidak Detect Data

1. Pastikan `http_port` di database sesuai dengan fake router port
2. Cek fake router masih running
3. Test manual: `curl http://localhost:8081/wifi`

### No Alerts

1. Pastikan Telegram token sudah configured
2. Cek threshold di `.env`
3. Review log NMS untuk errors

---

## 📝 Next Steps

1. ✅ Start fake routers
2. ✅ Add devices ke NMS
3. ✅ Configure Telegram alerts
4. ✅ Monitor dashboard
5. ✅ Test alert dengan simulasi down/high bandwidth

---

**Happy Testing! 🧪📊**
