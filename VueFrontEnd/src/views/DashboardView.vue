<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="header">
      <div class="container">
        <h1 class="logo">
          <span class="icon">📡</span>
          NMS Dashboard
        </h1>
        <div class="header-info">
          <span class="time">{{ currentTime }}</span>
          <span class="status-badge" :class="systemStatus">
            {{ systemStatus === 'online' ? '🟢 Online' : '🔴 Offline' }}
          </span>
        </div>
      </div>
    </header>

    <!-- Stats Cards -->
    <div class="container stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-info">
          <div class="stat-label">Total Devices</div>
          <div class="stat-value">{{ stats.total }}</div>
        </div>
      </div>

      <div class="stat-card online">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-label">Online</div>
          <div class="stat-value">{{ stats.up }}</div>
        </div>
      </div>

      <div class="stat-card offline">
        <div class="stat-icon">❌</div>
        <div class="stat-info">
          <div class="stat-label">Offline</div>
          <div class="stat-value">{{ stats.down }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-label">Avg Bandwidth</div>
          <div class="stat-value">{{ stats.avgBandwidth }} Mbps</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container main-content">
      <!-- Devices Table -->
      <div class="card">
        <div class="card-header">
          <h2>📱 Network Devices</h2>
          <button @click="showAddModal = true" class="btn btn-primary">
            ➕ Add Device
          </button>
        </div>

        <div class="devices-table">
          <table>
            <thead>
              <tr>
                <th>Device Name</th>
                <th>IP Address</th>
                <th>Type</th>
                <th>Location</th>
                <th>Status</th>
                <th>Bandwidth</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="device in devices" :key="device.id" :class="{'row-down': device.status === 'down'}">
                <td>
                  <strong>{{ device.name }}</strong>
                </td>
                <td>
                  <code>{{ device.ip_address }}</code>
                </td>
                <td>
                  <span class="badge">{{ device.device_type || 'router' }}</span>
                </td>
                <td>{{ device.location || '-' }}</td>
                <td>
                  <span class="status-dot" :class="device.status"></span>
                  {{ device.status }}
                </td>
                <td>
                  <div v-if="deviceBandwidth[device.id]">
                    <div class="bandwidth-mini">
                      ↓ {{ deviceBandwidth[device.id].in_mbps || 0 }} Mbps
                    </div>
                    <div class="bandwidth-mini">
                      ↑ {{ deviceBandwidth[device.id].out_mbps || 0 }} Mbps
                    </div>
                  </div>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <button @click="viewDetails(device)" class="btn btn-sm btn-info">
                    👁️ View
                  </button>
                  <button @click="deleteDevice(device.id)" class="btn btn-sm btn-danger">
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="devices.length === 0" class="empty-state">
            <div class="empty-icon">📭</div>
            <p>No devices found. Add a device to start monitoring.</p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-grid">
        <!-- Bandwidth Chart -->
        <div class="card">
          <div class="card-header">
            <h3>📈 Bandwidth Usage</h3>
            <select v-model="selectedDeviceId" @change="updateChart" class="select-device">
              <option value="">All Devices</option>
              <option v-for="device in devices.filter(d => d.status === 'up')" :key="device.id" :value="device.id">
                {{ device.name }}
              </option>
            </select>
          </div>
          <div class="chart-container">
            <canvas ref="bandwidthChart"></canvas>
          </div>
        </div>

        <!-- Device Status Pie Chart -->
        <div class="card">
          <div class="card-header">
            <h3>🔄 Device Status</h3>
          </div>
          <div class="chart-container">
            <canvas ref="statusChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Device Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Add New Device</h2>
          <button @click="showAddModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Device Name *</label>
            <input v-model="newDevice.name" type="text" placeholder="e.g., Router Office 1" />
          </div>
          <div class="form-group">
            <label>IP Address *</label>
            <input v-model="newDevice.ip_address" type="text" placeholder="e.g., 192.168.1.1" />
          </div>
          <div class="form-group">
            <label>Device Type</label>
            <select v-model="newDevice.device_type">
              <option value="router">Router</option>
              <option value="wifi_ap">WiFi AP</option>
              <option value="switch">Switch</option>
              <option value="server">Server</option>
            </select>
          </div>
          <div class="form-group">
            <label>Location</label>
            <input v-model="newDevice.location" type="text" placeholder="e.g., Lantai 1" />
          </div>
          <div class="form-group">
            <label>HTTP Port (for fake routers)</label>
            <input v-model.number="newDevice.http_port" type="number" placeholder="e.g., 8081" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAddModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="addDevice" class="btn btn-primary">Add Device</button>
        </div>
      </div>
    </div>

    <!-- Device Details Modal -->
    <div v-if="selectedDevice" class="modal-overlay" @click.self="selectedDevice = null">
      <div class="modal modal-large">
        <div class="modal-header">
          <h2>{{ selectedDevice.name }} - Details</h2>
          <button @click="selectedDevice = null" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div class="device-details">
            <div class="detail-row">
              <span class="detail-label">IP Address:</span>
              <code>{{ selectedDevice.ip_address }}</code>
            </div>
            <div class="detail-row">
              <span class="detail-label">Type:</span>
              <span class="badge">{{ selectedDevice.device_type }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Location:</span>
              {{ selectedDevice.location || '-' }}
            </div>
            <div class="detail-row">
              <span class="detail-label">Status:</span>
              <span class="status-dot" :class="selectedDevice.status"></span>
              {{ selectedDevice.status }}
            </div>
            <div class="detail-row">
              <span class="detail-label">Last Checked:</span>
              {{ formatDate(selectedDevice.last_checked) }}
            </div>
          </div>

          <!-- Bandwidth Info -->
          <div v-if="deviceBandwidth[selectedDevice.id]" class="bandwidth-details">
            <h3>Current Bandwidth</h3>
            <div class="bandwidth-cards">
              <div class="bandwidth-card download">
                <div class="bandwidth-icon">⬇️</div>
                <div class="bandwidth-value">
                  {{ deviceBandwidth[selectedDevice.id].in_mbps || 0 }} Mbps
                </div>
                <div class="bandwidth-label">Download</div>
              </div>
              <div class="bandwidth-card upload">
                <div class="bandwidth-icon">⬆️</div>
                <div class="bandwidth-value">
                  {{ deviceBandwidth[selectedDevice.id].out_mbps || 0 }} Mbps
                </div>
                <div class="bandwidth-label">Upload</div>
              </div>
              <div class="bandwidth-card total">
                <div class="bandwidth-icon">📊</div>
                <div class="bandwidth-value">
                  {{ deviceBandwidth[selectedDevice.id].total_mbps || 0 }} Mbps
                </div>
                <div class="bandwidth-label">Total</div>
              </div>
            </div>
          </div>

          <!-- WiFi Info -->
          <div v-if="deviceWifi[selectedDevice.id]" class="wifi-details">
            <h3>WiFi Information</h3>
            <div class="wifi-info-grid">
              <div class="wifi-info-item">
                <span class="wifi-label">SSID:</span>
                <strong>{{ deviceWifi[selectedDevice.id].ssid }}</strong>
              </div>
              <div class="wifi-info-item">
                <span class="wifi-label">Connected Clients:</span>
                <strong>{{ deviceWifi[selectedDevice.id].connected_clients }}</strong>
              </div>
              <div class="wifi-info-item">
                <span class="wifi-label">Signal Strength:</span>
                <strong>{{ deviceWifi[selectedDevice.id].signal_strength }} dBm</strong>
              </div>
              <div class="wifi-info-item">
                <span class="wifi-label">Channel:</span>
                <strong>{{ deviceWifi[selectedDevice.id].channel }}</strong>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="refreshDeviceData(selectedDevice.id)" class="btn btn-primary">
            🔄 Refresh
          </button>
          <button @click="selectedDevice = null" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// State
const devices = ref([])
const deviceBandwidth = ref({})
const deviceWifi = ref({})
const showAddModal = ref(false)
const selectedDevice = ref(null)
const selectedDeviceId = ref('')
const currentTime = ref('')
const systemStatus = ref('online')

const newDevice = ref({
  name: '',
  ip_address: '',
  device_type: 'router',
  location: '',
  http_port: null
})

// Charts
const bandwidthChart = ref(null)
const statusChart = ref(null)
let bandwidthChartInstance = null
let statusChartInstance = null
let refreshInterval = null

// Computed
const stats = computed(() => {
  const total = devices.value.length
  const up = devices.value.filter(d => d.status === 'up').length
  const down = devices.value.filter(d => d.status === 'down').length
  
  let totalBandwidth = 0
  let count = 0
  Object.values(deviceBandwidth.value).forEach(bw => {
    if (bw && bw.total_mbps) {
      totalBandwidth += bw.total_mbps
      count++
    }
  })
  const avgBandwidth = count > 0 ? (totalBandwidth / count).toFixed(2) : 0

  return { total, up, down, avgBandwidth }
})

// Methods
async function fetchDevices() {
  try {
    const response = await axios.get('/devices')
    devices.value = response.data
    systemStatus.value = 'online'
  } catch (error) {
    console.error('Error fetching devices:', error)
    systemStatus.value = 'offline'
  }
}

async function fetchBandwidth(deviceId) {
  try {
    const response = await axios.get(`/devices/${deviceId}/bandwidth`)
    if (response.data.success && response.data.bandwidth) {
      deviceBandwidth.value[deviceId] = response.data.bandwidth
    }
  } catch (error) {
    console.error(`Error fetching bandwidth for device ${deviceId}:`, error)
  }
}

async function fetchWifi(deviceId) {
  try {
    const response = await axios.get(`/devices/${deviceId}/wifi`)
    if (response.data.success && response.data.wifi) {
      deviceWifi.value[deviceId] = response.data.wifi
    }
  } catch (error) {
    console.error(`Error fetching WiFi for device ${deviceId}:`, error)
  }
}

async function addDevice() {
  if (!newDevice.value.name || !newDevice.value.ip_address) {
    alert('Please fill in required fields')
    return
  }

  try {
    await axios.post('/devices', newDevice.value)
    newDevice.value = {
      name: '',
      ip_address: '',
      device_type: 'router',
      location: '',
      http_port: null
    }
    showAddModal.value = false
    await fetchDevices()
    await fetchAllDeviceData()
  } catch (error) {
    console.error('Error adding device:', error)
    alert('Failed to add device')
  }
}

async function deleteDevice(deviceId) {
  if (!confirm('Are you sure you want to delete this device?')) return

  try {
    await axios.delete(`/devices/${deviceId}`)
    await fetchDevices()
    delete deviceBandwidth.value[deviceId]
    delete deviceWifi.value[deviceId]
  } catch (error) {
    console.error('Error deleting device:', error)
    alert('Failed to delete device')
  }
}

function viewDetails(device) {
  selectedDevice.value = device
  if (device.status === 'up') {
    refreshDeviceData(device.id)
  }
}

async function refreshDeviceData(deviceId) {
  await fetchBandwidth(deviceId)
  await fetchWifi(deviceId)
}

async function fetchAllDeviceData() {
  for (const device of devices.value) {
    if (device.status === 'up') {
      await fetchBandwidth(device.id)
      if (device.device_type === 'wifi_ap' || device.device_type === 'router') {
        await fetchWifi(device.id)
      }
    }
  }
  updateCharts()
}

function initBandwidthChart() {
  if (!bandwidthChart.value) return

  const ctx = bandwidthChart.value.getContext('2d')
  
  bandwidthChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Download (Mbps)',
          data: [],
          borderColor: '#4caf50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Upload (Mbps)',
          data: [],
          borderColor: '#2196f3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Bandwidth (Mbps)'
          }
        }
      }
    }
  })
}

function initStatusChart() {
  if (!statusChart.value) return

  const ctx = statusChart.value.getContext('2d')
  
  statusChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Online', 'Offline', 'Unknown'],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: [
          '#4caf50',
          '#f44336',
          '#9e9e9e'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        }
      }
    }
  })
}

function updateCharts() {
  updateBandwidthChart()
  updateStatusChart()
}

function updateBandwidthChart() {
  if (!bandwidthChartInstance) return

  const deviceList = selectedDeviceId.value 
    ? [devices.value.find(d => d.id == selectedDeviceId.value)]
    : devices.value.filter(d => d.status === 'up')

  const labels = deviceList.map(d => d.name)
  const downloadData = deviceList.map(d => {
    const bw = deviceBandwidth.value[d.id]
    return bw ? bw.in_mbps || 0 : 0
  })
  const uploadData = deviceList.map(d => {
    const bw = deviceBandwidth.value[d.id]
    return bw ? bw.out_mbps || 0 : 0
  })

  bandwidthChartInstance.data.labels = labels
  bandwidthChartInstance.data.datasets[0].data = downloadData
  bandwidthChartInstance.data.datasets[1].data = uploadData
  bandwidthChartInstance.update()
}

function updateStatusChart() {
  if (!statusChartInstance) return

  const up = devices.value.filter(d => d.status === 'up').length
  const down = devices.value.filter(d => d.status === 'down').length
  const unknown = devices.value.filter(d => d.status === 'unknown').length

  statusChartInstance.data.datasets[0].data = [up, down, unknown]
  statusChartInstance.update()
}

function updateChart() {
  updateBandwidthChart()
}

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('id-ID')
}

// Lifecycle
onMounted(async () => {
  await fetchDevices()
  await fetchAllDeviceData()
  
  // Initialize charts
  setTimeout(() => {
    initBandwidthChart()
    initStatusChart()
    updateCharts()
  }, 100)

  // Update time
  updateTime()
  setInterval(updateTime, 1000)

  // Refresh data every 30 seconds
  refreshInterval = setInterval(async () => {
    await fetchDevices()
    await fetchAllDeviceData()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (bandwidthChartInstance) {
    bandwidthChartInstance.destroy()
  }
  if (statusChartInstance) {
    statusChartInstance.destroy()
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.8rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  font-size: 2rem;
}

.header-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.time {
  font-size: 0.9rem;
  opacity: 0.9;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.status-badge.online {
  background: rgba(255,255,255,0.2);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem auto;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  gap: 1rem;
  align-items: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stat-card.online {
  border-left: 4px solid #4caf50;
}

.stat-card.offline {
  border-left: 4px solid #f44336;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.main-content {
  padding-bottom: 3rem;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2, .card-header h3 {
  margin: 0;
  color: #333;
}

.select-device {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
}

.devices-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #666;
  font-size: 0.9rem;
  text-transform: uppercase;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

tr:hover {
  background: #f8f9fa;
}

.row-down {
  background: #ffebee !important;
}

code {
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  background: #e3f2fd;
  color: #1976d2;
  display: inline-block;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-dot.up {
  background: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}

.status-dot.down {
  background: #f44336;
  box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.2);
}

.status-dot.unknown {
  background: #9e9e9e;
}

.bandwidth-mini {
  font-size: 0.85rem;
  color: #666;
}

.text-muted {
  color: #999;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  margin-right: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.chart-container {
  padding: 1.5rem;
  height: 300px;
  position: relative;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 2rem;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.modal-large {
  max-width: 800px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.btn-close:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.device-details {
  margin-bottom: 2rem;
}

.detail-row {
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-weight: 600;
  color: #666;
}

.bandwidth-details h3,
.wifi-details h3 {
  margin: 2rem 0 1rem 0;
  color: #333;
}

.bandwidth-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.bandwidth-card {
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
}

.bandwidth-card.download {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
}

.bandwidth-card.upload {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
}

.bandwidth-card.total {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
}

.bandwidth-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.bandwidth-value {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.bandwidth-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.wifi-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.wifi-info-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.wifi-label {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .bandwidth-cards {
    grid-template-columns: 1fr;
  }

  .wifi-info-grid {
    grid-template-columns: 1fr;
  }

  .devices-table {
    font-size: 0.9rem;
  }

  th, td {
    padding: 0.75rem 0.5rem;
  }
}
</style>
