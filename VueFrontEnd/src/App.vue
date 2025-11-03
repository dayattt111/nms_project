

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Network Monitoring Dashboard</h1>

    <!-- Input tambah perangkat -->
    <div class="mb-4">
      <input v-model="newDevice.name" placeholder="Nama perangkat" class="border p-2 mr-2" />
      <input v-model="newDevice.ip_address" placeholder="IP address" class="border p-2 mr-2" />
      <button @click="addDevice" class="bg-green-600 text-white px-3 py-2 rounded">Tambah</button>
    </div>

    <!-- Tabel perangkat -->
    <table border="1" cellpadding="8" class="w-full">
      <tr>
        <th>Nama</th>
        <th>IP</th>
        <th>Status</th>
        <th>Last Checked</th>
        <th>Aksi</th>
      </tr>
      <tr v-for="d in devices" :key="d.id">
        <td>{{ d.name }}</td>
        <td>{{ d.ip_address }}</td>
        <td :style="{ color: d.status === 'up' ? 'green' : 'red' }">
          {{ d.status }}
        </td>
        <td>{{ d.last_checked || '-' }}</td>
        <td>
          <button @click="showTraffic(d.ip_address)" class="bg-blue-500 text-white px-2 py-1 rounded mr-2">Lihat Trafik</button>
          <button @click="deleteDevice(d.id)" class="bg-red-500 text-white px-2 py-1 rounded">Hapus</button>
        </td>
      </tr>
    </table>

    <!-- Grafik Trafik -->
    <div v-if="trafficData" class="mt-6">
      <h2 class="text-xl font-bold mb-2">Trafik {{ trafficData.ip }}</h2>
      <canvas id="trafficChart"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { Chart } from 'chart.js/auto'

const API_URL = 'http://127.0.0.1:5000/devices'
const devices = ref([])
const newDevice = ref({ name: '', ip_address: '' })
const trafficData = ref(null)
let chart = null

async function fetchDevices() {
  const res = await axios.get(API_URL)
  devices.value = res.data
}

async function addDevice() {
  if (!newDevice.value.name || !newDevice.value.ip_address) return
  await axios.post(API_URL, newDevice.value)
  newDevice.value = { name: '', ip_address: '' }
  await fetchDevices()
}

async function deleteDevice(id) {
  await axios.delete(`${API_URL}/${id}`)
  await fetchDevices()
}

async function showTraffic(ip) {
  const res = await axios.get(`http://127.0.0.1:5000/traffic/${ip}`)
  trafficData.value = res.data
  renderChart(res.data)
}

function renderChart(data) {
  const ctx = document.getElementById('trafficChart')
  if (chart) chart.destroy()
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['In (Mbps)', 'Out (Mbps)'],
      datasets: [
        {
          label: `Trafik ${data.timestamp}`,
          data: [data.in_mbps, data.out_mbps],
          backgroundColor: ['#4CAF50', '#FF5722']
        }
      ]
    },
    options: {
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
}

onMounted(() => {
  fetchDevices()
  setInterval(fetchDevices, 10000)
})
</script>
