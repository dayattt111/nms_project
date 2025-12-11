# API Documentation - NMS System

## Base URL
```
http://localhost:5000/api
```

## Response Format
All responses are in JSON format with standard structure:
```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "error": null
}
```

---

## 📱 Device Management API

### 1. Get All Devices
**Endpoint:** `GET /api/devices`

**Description:** Retrieve list of all monitored devices

**Response:**
```json
[
  {
    "id": 1,
    "name": "Router Utama",
    "ip_address": "192.168.1.1",
    "device_type": "router",
    "status": "up",
    "last_checked": "2025-12-11 10:30:45",
    "location": "Data Center",
    "description": "Main router",
    "created_at": "2025-12-10 08:00:00"
  }
]
```

**cURL Example:**
```bash
curl http://localhost:5000/api/devices
```

---

### 2. Add New Device
**Endpoint:** `POST /api/devices`

**Description:** Add a new device to monitoring

**Request Body:**
```json
{
  "name": "Router Office",
  "ip_address": "192.168.2.1",
  "device_type": "router",
  "location": "Office Floor 1",
  "description": "Office main router",
  "snmp_community": "public",
  "interface_index": 2
}
```

**Response:**
```json
{
  "message": "Device added successfully",
  "device_id": 2
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Router Office",
    "ip_address": "192.168.2.1",
    "device_type": "router",
    "location": "Office Floor 1"
  }'
```

---

### 3. Update Device
**Endpoint:** `PUT /api/devices/<device_id>`

**Description:** Update device information

**Request Body:**
```json
{
  "name": "Router Office Updated",
  "ip_address": "192.168.2.1",
  "location": "Office Floor 2"
}
```

**Response:**
```json
{
  "message": "Device updated successfully"
}
```

**cURL Example:**
```bash
curl -X PUT http://localhost:5000/api/devices/2 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Router Office Updated",
    "location": "Office Floor 2"
  }'
```

---

### 4. Delete Device
**Endpoint:** `DELETE /api/devices/<device_id>`

**Description:** Remove device from monitoring

**Response:**
```json
{
  "message": "Device deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:5000/api/devices/2
```

---

## 📊 Monitoring API

### 5. Get Device Bandwidth
**Endpoint:** `GET /api/monitoring/bandwidth/<device_id>`

**Description:** Get real-time bandwidth usage of a device via SNMP

**Query Parameters:**
- `interface` (optional): Interface index (default: 2)

**Response:**
```json
{
  "success": true,
  "device": {
    "id": 1,
    "name": "Router Utama",
    "ip_address": "192.168.1.1"
  },
  "bandwidth": {
    "ip": "192.168.1.1",
    "interface_index": 2,
    "in_bytes_per_sec": 1048576,
    "out_bytes_per_sec": 524288,
    "in_mbps": 8.0,
    "out_mbps": 4.0,
    "total_mbps": 12.0,
    "timestamp": "2025-12-11T10:30:45"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/monitoring/bandwidth/1
curl http://localhost:5000/api/monitoring/bandwidth/1?interface=3
```

---

### 6. Get Device Interfaces
**Endpoint:** `GET /api/monitoring/interfaces/<device_id>`

**Description:** List all available network interfaces on device

**Response:**
```json
{
  "success": true,
  "device": {
    "id": 1,
    "name": "Router Utama",
    "ip_address": "192.168.1.1"
  },
  "interfaces": [
    {
      "index": 1,
      "description": "lo",
      "status": "up"
    },
    {
      "index": 2,
      "description": "eth0",
      "status": "up"
    },
    {
      "index": 3,
      "description": "eth1",
      "status": "down"
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/monitoring/interfaces/1
```

---

### 7. Get All Devices Bandwidth
**Endpoint:** `GET /api/monitoring/bandwidth/all`

**Description:** Get bandwidth data from all active devices

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "device": {
        "id": 1,
        "name": "Router Utama",
        "ip_address": "192.168.1.1"
      },
      "bandwidth": {
        "in_mbps": 8.0,
        "out_mbps": 4.0,
        "total_mbps": 12.0,
        "timestamp": "2025-12-11T10:30:45"
      }
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/monitoring/bandwidth/all
```

---

### 8. Check Bandwidth Threshold
**Endpoint:** `POST /api/monitoring/check-bandwidth`

**Description:** Check bandwidth against thresholds and send alerts if exceeded

**Request Body:**
```json
{
  "device_id": 1,
  "threshold_high": 80,
  "threshold_low": 1
}
```

**Response:**
```json
{
  "success": true,
  "device": {
    "id": 1,
    "name": "Router Utama",
    "ip_address": "192.168.1.1"
  },
  "bandwidth": {
    "in_mbps": 85.5,
    "out_mbps": 45.2,
    "total_mbps": 130.7
  },
  "alerts_sent": ["high_bandwidth_alert"]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/monitoring/check-bandwidth \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "threshold_high": 80,
    "threshold_low": 1
  }'
```

---

## 🔧 Zabbix Integration API

### 9. Get Zabbix Hosts
**Endpoint:** `GET /api/zabbix/hosts`

**Description:** Retrieve list of hosts from Zabbix server

**Response:**
```json
{
  "success": true,
  "count": 5,
  "hosts": [
    {
      "hostid": "10084",
      "host": "Zabbix server",
      "name": "Zabbix server",
      "status": "0",
      "interfaces": [
        {
          "ip": "127.0.0.1",
          "port": "10050"
        }
      ]
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/zabbix/hosts
```

---

### 10. Get Zabbix Host Items
**Endpoint:** `GET /api/zabbix/host/<hostid>/items`

**Description:** Get monitoring items (metrics) for specific Zabbix host

**Response:**
```json
{
  "success": true,
  "hostid": "10084",
  "count": 25,
  "items": [
    {
      "itemid": "23298",
      "name": "CPU utilization",
      "key_": "system.cpu.util",
      "lastvalue": "15.5",
      "units": "%"
    },
    {
      "itemid": "23299",
      "name": "Network traffic in on eth0",
      "key_": "net.if.in[eth0]",
      "lastvalue": "1048576",
      "units": "bps"
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/zabbix/host/10084/items
```

---

### 11. Get Zabbix Host Bandwidth
**Endpoint:** `GET /api/zabbix/host/<hostid>/bandwidth`

**Description:** Get bandwidth data from Zabbix for specific host

**Query Parameters:**
- `interface` (optional): Interface name (default: eth0)

**Response:**
```json
{
  "success": true,
  "data": {
    "hostid": "10084",
    "interface": "eth0",
    "timestamp": "2025-12-11T10:30:45",
    "traffic_in": 1048576,
    "traffic_out": 524288,
    "traffic_in_bps": 8388608,
    "traffic_out_bps": 4194304,
    "traffic_in_formatted": "1.00 MB",
    "traffic_out_formatted": "512.00 KB",
    "traffic_in_bps_formatted": "8.00 Mbps",
    "traffic_out_bps_formatted": "4.00 Mbps"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/zabbix/host/10084/bandwidth
curl http://localhost:5000/api/zabbix/host/10084/bandwidth?interface=eth1
```

---

### 12. Get Zabbix Triggers
**Endpoint:** `GET /api/zabbix/triggers`

**Description:** Get active triggers (alerts) from Zabbix

**Query Parameters:**
- `severity` (optional): Minimum severity level (0-5, default: 2)
  - 0: Not classified
  - 1: Information
  - 2: Warning
  - 3: Average
  - 4: High
  - 5: Disaster

**Response:**
```json
{
  "success": true,
  "count": 3,
  "triggers": [
    {
      "triggerid": "13491",
      "description": "High CPU utilization on {HOST.NAME}",
      "priority": "4",
      "lastchange": "1702290645",
      "value": "1",
      "hosts": [
        {
          "hostid": "10084",
          "host": "Zabbix server",
          "name": "Zabbix server"
        }
      ]
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/zabbix/triggers
curl http://localhost:5000/api/zabbix/triggers?severity=4
```

---

### 13. Sync Zabbix Hosts to Database
**Endpoint:** `POST /api/monitoring/sync-zabbix`

**Description:** Import hosts from Zabbix into local database

**Response:**
```json
{
  "success": true,
  "message": "Synced 5 hosts from Zabbix",
  "total_hosts": 10
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/monitoring/sync-zabbix
```

---

## 📈 Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 404  | Not Found |
| 500  | Internal Server Error |

---

## 🔐 Authentication

Current version does not implement authentication. For production use, consider adding:
- JWT tokens
- API keys
- OAuth 2.0
- Basic authentication with HTTPS

---

## 📝 Notes

### SNMP Requirements
- Device must have SNMP enabled
- Correct community string configured
- Port 161 (UDP) accessible
- SNMP v2c or v3 supported

### Bandwidth Calculation
Bandwidth is calculated by:
1. Get counter value at T1
2. Wait 1 second
3. Get counter value at T2
4. Calculate: (T2 - T1) bytes/second
5. Convert to Mbps: (bytes/sec * 8) / (1024 * 1024)

### Interface Index
Common interface indexes:
- 1: Loopback (lo)
- 2: First Ethernet (eth0)
- 3: Second Ethernet (eth1)
- Use `/api/monitoring/interfaces/<device_id>` to discover

### Telegram Alerts
Automatic alerts are sent for:
- Device status changes (up ↔️ down)
- Bandwidth exceeds high threshold
- Bandwidth drops below low threshold
- Zabbix triggers (severity ≥ 3)
- Periodic summary reports

---

## 🧪 Testing Examples

### Python
```python
import requests

# Get devices
response = requests.get('http://localhost:5000/api/devices')
devices = response.json()

# Add device
new_device = {
    'name': 'Test Router',
    'ip_address': '192.168.1.100',
    'device_type': 'router'
}
response = requests.post('http://localhost:5000/api/devices', json=new_device)

# Get bandwidth
response = requests.get('http://localhost:5000/api/monitoring/bandwidth/1')
bandwidth = response.json()
```

### JavaScript
```javascript
// Get devices
fetch('http://localhost:5000/api/devices')
  .then(response => response.json())
  .then(data => console.log(data));

// Add device
fetch('http://localhost:5000/api/devices', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Test Router',
    ip_address: '192.168.1.100',
    device_type: 'router'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

**For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)**
