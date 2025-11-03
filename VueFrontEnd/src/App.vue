<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const devices = ref([])

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:5000/devices')
  devices.value = res.data
})
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Network Monitoring Dashboard</h1>
    <table border="1" cellpadding="8">
      <tr>
        <th>Device</th>
        <th>IP Address</th>
        <th>Status</th>
        <th>Last Checked</th>
      </tr>
      <tr v-for="d in devices" :key="d.id">
        <td>{{ d.name }}</td>
        <td>{{ d.ip_address }}</td>
        <td :style="{ color: d.status === 'up' ? 'green' : 'red' }">
          {{ d.status }}
        </td>
        <td>{{ d.last_checked }}</td>
      </tr>
    </table>
  </div>
</template>
