#!/usr/bin/env python3
"""
Fake Router/Server Simulator untuk Testing NMS
Mensimulasikan router dengan SNMP dan HTTP server
"""

import http.server
import socketserver
import threading
import time
import random
from datetime import datetime
import json

class FakeRouterHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler untuk fake router"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                'device': 'Fake Router',
                'status': 'online',
                'uptime': int(time.time() - router_start_time),
                'cpu_usage': random.randint(10, 80),
                'memory_usage': random.randint(20, 70),
                'interfaces': {
                    'eth0': {
                        'status': 'up',
                        'speed': '1000Mbps',
                        'rx_bytes': random.randint(1000000, 10000000),
                        'tx_bytes': random.randint(500000, 5000000)
                    },
                    'wlan0': {
                        'status': 'up',
                        'speed': '300Mbps',
                        'rx_bytes': random.randint(500000, 5000000),
                        'tx_bytes': random.randint(200000, 2000000),
                        'signal': random.randint(-70, -30),
                        'noise': random.randint(-90, -80)
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(status, indent=2).encode())
        
        elif self.path == '/wifi':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            wifi_info = {
                'ssid': 'FakeRouter-WiFi',
                'channel': 6,
                'frequency': '2.4GHz',
                'connected_clients': random.randint(1, 10),
                'signal_strength': random.randint(-70, -30),
                'bandwidth_usage': {
                    'download': round(random.uniform(1, 50), 2),  # Mbps
                    'upload': round(random.uniform(0.5, 20), 2)   # Mbps
                },
                'security': 'WPA2-PSK',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(wifi_info, indent=2).encode())
        
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Fake Router Web Interface</title>
                <style>
                    body { font-family: Arial; margin: 40px; background: #f0f0f0; }
                    .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    .endpoint { background: #e8f5e9; padding: 10px; margin: 10px 0; border-radius: 4px; }
                    code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌐 Fake Router Web Interface</h1>
                    <p>This is a simulated router for testing NMS system</p>
                    
                    <h2>Available Endpoints:</h2>
                    <div class="endpoint">
                        <strong>GET /status</strong><br>
                        Returns router status, CPU, memory, and interface statistics
                    </div>
                    <div class="endpoint">
                        <strong>GET /wifi</strong><br>
                        Returns WiFi information including signal strength and bandwidth
                    </div>
                    
                    <h2>SNMP Information:</h2>
                    <p>SNMP Community: <code>public</code></p>
                    <p>SNMP Port: <code>161</code> (simulated)</p>
                    
                    <h2>Test URLs:</h2>
                    <p><a href="/status">View Status JSON</a></p>
                    <p><a href="/wifi">View WiFi Info JSON</a></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")


class FakeRouter:
    """Fake Router simulator"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        
    def start(self):
        """Start the fake router server"""
        global router_start_time
        router_start_time = time.time()
        
        self.server = socketserver.TCPServer(("", self.port), FakeRouterHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.running = True
        
        print(f"🌐 Fake Router started on http://localhost:{self.port}")
        print(f"📊 Status API: http://localhost:{self.port}/status")
        print(f"📡 WiFi API: http://localhost:{self.port}/wifi")
        
    def stop(self):
        """Stop the fake router server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("🛑 Fake Router stopped")


def simulate_network_activity():
    """Simulate changing network conditions"""
    conditions = ['normal', 'high_traffic', 'low_signal', 'packet_loss']
    
    while True:
        condition = random.choice(conditions)
        
        if condition == 'normal':
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Network: Normal operation")
        elif condition == 'high_traffic':
            print(f"⚠️  [{datetime.now().strftime('%H:%M:%S')}] Network: High traffic detected")
        elif condition == 'low_signal':
            print(f"📶 [{datetime.now().strftime('%H:%M:%S')}] WiFi: Low signal strength")
        elif condition == 'packet_loss':
            print(f"📉 [{datetime.now().strftime('%H:%M:%S')}] Network: Packet loss detected")
        
        time.sleep(random.randint(30, 120))


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Fake Router/Server Simulator")
    print("=" * 50)
    print()
    
    # Start fake router
    router = FakeRouter(port=8080)
    router.start()
    
    print()
    print("=" * 50)
    print("📝 How to test with NMS:")
    print("=" * 50)
    print("1. Add device to NMS:")
    print("   IP: 127.0.0.1 or localhost")
    print("   Type: router")
    print()
    print("2. The device will respond to:")
    print("   - ICMP ping")
    print("   - HTTP requests on port 8080")
    print()
    print("3. Test endpoints:")
    print("   curl http://localhost:8080/status")
    print("   curl http://localhost:8080/wifi")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    # Start network simulation
    sim_thread = threading.Thread(target=simulate_network_activity)
    sim_thread.daemon = True
    sim_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down fake router...")
        router.stop()
        print("✅ Shutdown complete")
