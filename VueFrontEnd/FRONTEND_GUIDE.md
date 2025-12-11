# Frontend UI Guide - NMS Dashboard

## 📋 Fitur Dashboard

### 1. **Header & Real-time Status**
- Logo dan nama aplikasi
- Waktu real-time yang terupdate setiap detik
- Status sistem (Online/Offline)

### 2. **Statistics Cards**
- 🖥️ **Total Devices**: Jumlah semua perangkat
- ✅ **Online**: Jumlah perangkat yang up
- ❌ **Offline**: Jumlah perangkat yang down
- 📊 **Avg Bandwidth**: Rata-rata bandwidth semua perangkat

### 3. **Device Management Table**
- Tabel lengkap dengan informasi:
  - Device Name
  - IP Address
  - Device Type (router, wifi_ap, switch, server)
  - Location
  - Status dengan indikator visual (🟢/🔴)
  - Bandwidth real-time (Download/Upload)
- **Actions**:
  - 👁️ View: Melihat detail lengkap perangkat
  - 🗑️ Delete: Menghapus perangkat
  - ➕ Add Device: Tombol untuk menambah perangkat baru

### 4. **Traffic Visualization Charts**

#### Bandwidth Usage Chart (Line Chart)
- Grafik line chart untuk monitoring bandwidth
- Menampilkan Download (hijau) dan Upload (biru)
- Filter per device atau semua device
- Auto-update setiap 30 detik

#### Device Status Pie Chart
- Grafik doughnut menampilkan proporsi:
  - Online (hijau)
  - Offline (merah)
  - Unknown (abu-abu)
- Real-time update berdasarkan status device

### 5. **Add Device Modal**
Form untuk menambah perangkat baru:
- Device Name (required)
- IP Address (required)
- Device Type (dropdown: router, wifi_ap, switch, server)
- Location (optional)
- HTTP Port (untuk fake routers)

### 6. **Device Details Modal**
Informasi lengkap saat klik "View":

**Basic Info:**
- IP Address
- Device Type
- Location
- Status
- Last Checked Time

**Bandwidth Details** (jika device online):
- ⬇️ Download speed (Mbps)
- ⬆️ Upload speed (Mbps)
- 📊 Total bandwidth (Mbps)
- Dengan card visual berwarna

**WiFi Information** (jika device adalah WiFi AP/Router):
- SSID
- Connected Clients
- Signal Strength (dBm)
- Channel

### 7. **Auto-Refresh System**
- Data di-refresh otomatis setiap 30 detik
- Clock updates setiap 1 detik
- Chart auto-update setiap kali data baru masuk

## 🎨 Design Features

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success/Online**: Green (#4caf50)
- **Error/Offline**: Red (#f44336)
- **Info**: Blue (#2196f3)
- **Background**: Light gray (#f5f7fa)

### UI Elements
- ✨ Smooth animations dan transitions
- 🎯 Hover effects pada cards dan buttons
- 📱 Responsive design (mobile-friendly)
- 🌈 Visual status indicators dengan dots dan colors
- 💫 Box shadows untuk depth

### Interactive Elements
- Hover animations pada cards (translateY effect)
- Button hover effects
- Modal overlays dengan backdrop blur
- Table row highlighting
- Chart tooltips

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
cd VueFrontEnd
npm install
```

### 2. Jalankan Backend Terlebih Dahulu
```bash
cd FlaskBackend
python app.py
```
Backend akan berjalan di `http://localhost:5000`

### 3. Jalankan Frontend Development Server
```bash
cd VueFrontEnd
npm run dev
```
Frontend akan berjalan di `http://localhost:5173`

### 4. Build untuk Production
```bash
npm run build
```
Output akan berada di folder `dist/`

## 📊 Integrasi dengan Backend

Dashboard terintegrasi dengan Flask Backend API:

### API Endpoints yang Digunakan:
- `GET /api/devices` - Fetch semua devices
- `POST /api/devices` - Tambah device baru
- `PUT /api/devices/:id` - Update device
- `DELETE /api/devices/:id` - Hapus device
- `GET /api/devices/:id/bandwidth` - Get bandwidth info
- `GET /api/devices/:id/wifi` - Get WiFi info

### Axios Configuration
Base URL sudah dikonfigurasi di `main.js`:
```javascript
axios.defaults.baseURL = 'http://localhost:5000/api'
```

## 🧪 Testing dengan Fake Routers

### Menjalankan Fake Routers:
```bash
cd FlaskBackend
python fake_multiple_routers.py
```

### Tambah Fake Routers di Dashboard:
1. Klik tombol "➕ Add Device"
2. Isi data:
   - **Router-Office-1**:
     - IP: localhost
     - HTTP Port: 8081
     - Type: router
   - **Router-Office-2**:
     - IP: localhost
     - HTTP Port: 8082
     - Type: router
   - **AP-Meeting-Room**:
     - IP: localhost
     - HTTP Port: 8083
     - Type: wifi_ap

3. Lihat dashboard menampilkan data real-time dari fake routers

## 📱 Responsive Breakpoints

- **Desktop**: > 768px (Grid layouts, side-by-side charts)
- **Tablet**: 768px (Adjusted grid)
- **Mobile**: < 768px (Single column, compact tables)

### Mobile Optimizations:
- Charts stack vertically
- Bandwidth cards stack vertically
- Table font size reduced
- Padding adjusted for smaller screens

## 🔄 Real-time Updates

### Auto-refresh Intervals:
- **Device Status**: 30 seconds
- **Bandwidth Data**: 30 seconds
- **Clock Display**: 1 second
- **Charts**: Update setelah data baru masuk

### Manual Refresh:
- Button "🔄 Refresh" di Device Details modal
- Refresh individual device data on-demand

## 💡 Tips Penggunaan

1. **Monitoring Traffic**: 
   - Gunakan filter dropdown di Bandwidth Chart untuk fokus pada device tertentu
   - Chart akan auto-scale berdasarkan nilai bandwidth

2. **Tambah Multiple Devices**:
   - Tambahkan semua fake routers untuk simulasi lengkap
   - Bisa juga tambah device fisik dengan IP address real

3. **Check Device Details**:
   - Klik "View" untuk info lengkap
   - Berguna untuk troubleshooting device offline

4. **WiFi Monitoring**:
   - Device type "wifi_ap" atau "router" akan menampilkan WiFi info
   - Monitor jumlah client dan signal strength

## 🎯 Next Steps

Fitur yang bisa ditambahkan:
- [ ] Alert notifications display
- [ ] Historical data charts (time series)
- [ ] Device grouping by location
- [ ] Export data to CSV/Excel
- [ ] Dark mode toggle
- [ ] User authentication
- [ ] Custom alert thresholds per device
- [ ] WebSocket for real-time push updates

## 🐛 Troubleshooting

### Problem: Data tidak muncul
**Solution**: 
1. Pastikan backend sudah jalan di port 5000
2. Check console browser untuk errors
3. Verify CORS enabled di backend

### Problem: Chart tidak muncul
**Solution**:
1. Pastikan Chart.js sudah terinstall: `npm install chart.js`
2. Clear cache dan refresh browser
3. Check browser console untuk errors

### Problem: Device status selalu "down"
**Solution**:
1. Pastikan fake routers berjalan
2. Check HTTP Port di device configuration
3. Verify backend bisa poll device HTTP API

## 📝 File Structure

```
VueFrontEnd/
├── src/
│   ├── views/
│   │   └── DashboardView.vue    # Main dashboard UI (lengkap)
│   ├── router/
│   │   └── index.js              # Route configuration
│   ├── App.vue                   # Root component
│   └── main.js                   # App initialization + axios config
├── package.json                  # Dependencies
└── FRONTEND_GUIDE.md            # This file
```

## 🎨 Customization

### Mengubah Warna Theme:
Edit di `DashboardView.vue`, cari section:
```css
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Mengubah Refresh Interval:
Edit di `DashboardView.vue`, function `onMounted`:
```javascript
refreshInterval = setInterval(async () => {
  await fetchDevices()
  await fetchAllDeviceData()
}, 30000) // Change 30000 to desired milliseconds
```

### Menambah Chart Type:
Import chart type baru di script setup:
```javascript
import { Chart, registerables } from 'chart.js'
```

Semua chart types sudah available: line, bar, pie, doughnut, radar, polar area.

---

**Developed for NMS DCC Project**  
Dashboard monitoring real-time untuk WiFi dan Network Devices 🚀
