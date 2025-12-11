#!/usr/bin/env python3
"""
Multiple Fake Routers Simulator
Mensimulasikan beberapa router/AP dengan karakteristik berbeda
"""

import http.server
import socketserver
import threading
import time
import random
from datetime import datetime
import json

router_configs = [
    {
        'name': 'Router-Office-1',
        'port': 8081,
        'ip': '127.0.0.1',
        'ssid': 'Office-WiFi-1',
        'location': 'Lantai 1',
        'device_type': 'router',
        'base_bandwidth': 50,  # Mbps
        'reliability': 0.95  # 95% uptime
    },
    {
        'name': 'Router-Office-2',
        'port': 8082,
        'ip': '127.0.0.1',
        'ssid': 'Office-WiFi-2',
        'location': 'Lantai 2',
        'device_type': 'router',
        'base_bandwidth': 30,
        'reliability': 0.90
    },
    {
        'name': 'AP-Meeting-Room',
        'port': 8083,
        'ip': '127.0.0.1',
        'ssid': 'Meeting-WiFi',
        'location': 'Meeting Room',
        'device_type': 'access_point',
        'base_bandwidth': 20,
        'reliability': 0.85
    }
]

router_start_times = {}


class FakeRouterHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler untuk fake router"""
    
    router_config = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            self.send_status_response()
        elif self.path == '/wifi':
            self.send_wifi_response()
        elif self.path == '/api/info':
            self.send_info_response()
        else:
            self.send_home_page()
    
    def send_status_response(self):
        """Send router status"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        config = self.router_config
        uptime = int(time.time() - router_start_times.get(config['port'], time.time()))
        
        # Simulate occasional issues
        is_online = random.random() < config['reliability']
        
        status = {
            'device': config['name'],
            'location': config['location'],
            'device_type': config['device_type'],
            'status': 'online' if is_online else 'degraded',
            'uptime_seconds': uptime,
            'uptime_formatted': f"{uptime // 3600}h {(uptime % 3600) // 60}m",
            'cpu_usage': random.randint(10, 90) if is_online else random.randint(80, 100),
            'memory_usage': random.randint(20, 70) if is_online else random.randint(70, 95),
            'temperature': random.randint(35, 65),
            'interfaces': {
                'eth0': {
                    'name': 'WAN',
                    'status': 'up' if is_online else 'degraded',
                    'speed': '1000Mbps',
                    'rx_bytes': random.randint(1000000, 50000000),
                    'tx_bytes': random.randint(500000, 25000000),
                    'rx_packets': random.randint(10000, 100000),
                    'tx_packets': random.randint(5000, 50000),
                    'errors': random.randint(0, 10) if not is_online else 0
                },
                'wlan0': {
                    'name': 'WiFi 2.4GHz',
                    'status': 'up' if is_online else 'degraded',
                    'speed': '300Mbps',
                    'rx_bytes': random.randint(500000, 20000000),
                    'tx_bytes': random.randint(200000, 10000000),
                    'rx_packets': random.randint(5000, 50000),
                    'tx_packets': random.randint(2000, 25000),
                    'signal': random.randint(-70, -30) if is_online else random.randint(-80, -70),
                    'noise': random.randint(-90, -80),
                    'errors': random.randint(0, 5) if not is_online else 0
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode())
    
    def send_wifi_response(self):
        """Send WiFi information"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        config = self.router_config
        is_online = random.random() < config['reliability']
        
        # Simulate bandwidth variation
        bandwidth_factor = random.uniform(0.5, 1.2) if is_online else random.uniform(0.1, 0.3)
        
        wifi_info = {
            'ssid': config['ssid'],
            'device': config['name'],
            'location': config['location'],
            'channel': random.choice([1, 6, 11]),
            'frequency': '2.4GHz',
            'connected_clients': random.randint(1, 15) if is_online else random.randint(0, 3),
            'signal_strength': random.randint(-70, -30) if is_online else random.randint(-85, -70),
            'bandwidth_usage': {
                'download_mbps': round(config['base_bandwidth'] * bandwidth_factor, 2),
                'upload_mbps': round(config['base_bandwidth'] * 0.3 * bandwidth_factor, 2),
                'total_mbps': round(config['base_bandwidth'] * 1.3 * bandwidth_factor, 2)
            },
            'security': 'WPA2-PSK',
            'quality': 'good' if is_online and bandwidth_factor > 0.7 else 'degraded',
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(wifi_info, indent=2).encode())
    
    def send_info_response(self):
        """Send device info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        config = self.router_config
        
        info = {
            'device_name': config['name'],
            'model': 'Fake Router v1.0',
            'location': config['location'],
            'ip_address': config['ip'],
            'port': config['port'],
            'ssid': config['ssid'],
            'firmware_version': '1.0.0',
            'mac_address': f"00:11:22:33:{config['port'] % 100:02d}:00",
            'capabilities': ['wifi', 'ethernet', 'http_api', 'ping'],
            'endpoints': [
                '/status - Device status and interfaces',
                '/wifi - WiFi information',
                '/api/info - Device information'
            ]
        }
        
        self.wfile.write(json.dumps(info, indent=2).encode())
    
    def send_home_page(self):
        """Send home page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        config = self.router_config
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config['name']} - Web Interface</title>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{ 
                    max-width: 800px;
                    margin: 0 auto;
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                h1 {{ 
                    color: #667eea;
                    margin-top: 0;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }}
                .info-box {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                }}
                .endpoint {{ 
                    background: #e8f5e9; 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-radius: 6px;
                    border-left: 4px solid #4caf50;
                }}
                .endpoint strong {{
                    color: #2e7d32;
                }}
                code {{ 
                    background: #f5f5f5; 
                    padding: 3px 8px; 
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    color: #d63384;
                }}
                a {{
                    color: #667eea;
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    background: #667eea;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 {config['name']}</h1>
                <span class="badge">{config['device_type'].upper()}</span>
                
                <div class="info-box">
                    <strong>📍 Location:</strong> {config['location']}<br>
                    <strong>📡 WiFi SSID:</strong> {config['ssid']}<br>
                    <strong>🔌 Port:</strong> {config['port']}<br>
                    <strong>📊 Base Bandwidth:</strong> {config['base_bandwidth']} Mbps<br>
                    <strong>✅ Reliability:</strong> {config['reliability'] * 100}%
                </div>
                
                <h2>📡 Available Endpoints:</h2>
                <div class="endpoint">
                    <strong>GET /status</strong><br>
                    Returns device status, CPU, memory, and interface statistics
                </div>
                <div class="endpoint">
                    <strong>GET /wifi</strong><br>
                    Returns WiFi information including signal strength and bandwidth
                </div>
                <div class="endpoint">
                    <strong>GET /api/info</strong><br>
                    Returns device information and capabilities
                </div>
                
                <h2>🔧 SNMP Information:</h2>
                <div class="info-box">
                    <strong>Community:</strong> <code>public</code><br>
                    <strong>Port:</strong> <code>161</code> (simulated)
                </div>
                
                <h2>🧪 Test URLs:</h2>
                <p>
                    <a href="/status" target="_blank">📊 View Status JSON</a> |
                    <a href="/wifi" target="_blank">📡 View WiFi Info</a> |
                    <a href="/api/info" target="_blank">ℹ️ View Device Info</a>
                </p>
                
                <h2>🔗 NMS Integration:</h2>
                <div class="info-box">
                    <strong>Add to NMS:</strong><br>
                    <code>curl -X POST http://localhost:5000/api/devices -H "Content-Type: application/json" -d '{{"name":"{config['name']}","ip_address":"127.0.0.1","device_type":"{config['device_type']}","location":"{config['location']}"}}'</code>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.router_config['name']}] {format % args}")


def create_router_handler(config):
    """Create a handler with specific router config"""
    class ConfiguredHandler(FakeRouterHandler):
        router_config = config
    return ConfiguredHandler


def start_fake_router(config):
    """Start a fake router on specified port"""
    handler = create_router_handler(config)
    server = socketserver.TCPServer(("", config['port']), handler)
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    router_start_times[config['port']] = time.time()
    
    return server


def main():
    print("=" * 70)
    print("🚀 Starting Multiple Fake Routers/APs Simulator")
    print("=" * 70)
    print()
    
    servers = []
    
    # Start all fake routers
    for config in router_configs:
        try:
            server = start_fake_router(config)
            servers.append(server)
            print(f"✅ {config['name']}")
            print(f"   📍 Location: {config['location']}")
            print(f"   🌐 URL: http://localhost:{config['port']}")
            print(f"   📡 WiFi: {config['ssid']}")
            print()
        except Exception as e:
            print(f"❌ Failed to start {config['name']}: {e}")
            print()
    
    print("=" * 70)
    print("📝 How to add devices to NMS:")
    print("=" * 70)
    print()
    
    for config in router_configs:
        print(f"# Add {config['name']}")
        print(f"curl -X POST http://localhost:5000/api/devices \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{")
        print(f"    \"name\": \"{config['name']}\",")
        print(f"    \"ip_address\": \"127.0.0.1\",")
        print(f"    \"device_type\": \"{config['device_type']}\",")
        print(f"    \"location\": \"{config['location']}\",")
        print(f"    \"http_port\": {config['port']}")
        print(f"  }}'")
        print()
    
    print("=" * 70)
    print("🧪 Test endpoints:")
    print("=" * 70)
    for config in router_configs:
        print(f"\n{config['name']}:")
        print(f"  curl http://localhost:{config['port']}/status")
        print(f"  curl http://localhost:{config['port']}/wifi")
    
    print("\n" + "=" * 70)
    print("Press Ctrl+C to stop all servers")
    print("=" * 70)
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all fake routers...")
        for server in servers:
            server.shutdown()
        print("✅ All servers stopped")


if __name__ == "__main__":
    main()
