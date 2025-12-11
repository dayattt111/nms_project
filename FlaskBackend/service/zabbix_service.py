import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class ZabbixAPI:
    def __init__(self):
        self.url = os.getenv("ZABBIX_URL", "http://localhost/zabbix/api_jsonrpc.php")
        self.username = os.getenv("ZABBIX_USER", "Admin")
        self.password = os.getenv("ZABBIX_PASSWORD", "zabbix")
        self.token = None
        
    def authenticate(self):
        """Authenticate dan dapatkan auth token dari Zabbix"""
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": self.username,
                "password": self.password
            },
            "id": 1
        }
        
        try:
            response = requests.post(self.url, json=payload)
            result = response.json()
            
            if 'result' in result:
                self.token = result['result']
                print(f"✅ Zabbix authentication successful")
                return True
            else:
                print(f"❌ Zabbix authentication failed: {result.get('error', {}).get('data', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Error connecting to Zabbix: {e}")
            return False
    
    def get_hosts(self):
        """Ambil daftar host dari Zabbix"""
        if not self.token:
            self.authenticate()
        
        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "port"],
            },
            "auth": self.token,
            "id": 2
        }
        
        try:
            response = requests.post(self.url, json=payload)
            result = response.json()
            
            if 'result' in result:
                return result['result']
            else:
                print(f"❌ Error getting hosts: {result.get('error', {})}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_host_items(self, hostid):
        """Ambil items dari host tertentu"""
        if not self.token:
            self.authenticate()
        
        payload = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemid", "name", "key_", "lastvalue", "units"],
                "hostids": hostid,
                "search": {
                    "key_": ["net.if", "system"]
                },
                "searchByAny": True,
                "sortfield": "name"
            },
            "auth": self.token,
            "id": 3
        }
        
        try:
            response = requests.post(self.url, json=payload)
            result = response.json()
            
            if 'result' in result:
                return result['result']
            else:
                print(f"❌ Error getting items: {result.get('error', {})}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_bandwidth_data(self, hostid, interface="eth0"):
        """Ambil data bandwidth interface tertentu"""
        if not self.token:
            self.authenticate()
        
        # Key untuk traffic in/out di Zabbix
        items_to_get = [
            f"net.if.in[{interface}]",
            f"net.if.out[{interface}]"
        ]
        
        payload = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemid", "name", "key_", "lastvalue", "units", "prevvalue"],
                "hostids": hostid,
                "search": {
                    "key_": items_to_get
                },
                "searchByAny": True
            },
            "auth": self.token,
            "id": 4
        }
        
        try:
            response = requests.post(self.url, json=payload)
            result = response.json()
            
            if 'result' in result:
                bandwidth_data = {
                    "hostid": hostid,
                    "interface": interface,
                    "timestamp": datetime.now().isoformat(),
                    "traffic_in": 0,
                    "traffic_out": 0,
                    "traffic_in_bps": 0,
                    "traffic_out_bps": 0
                }
                
                for item in result['result']:
                    lastvalue = float(item.get('lastvalue', 0))
                    
                    if 'in[' in item['key_']:
                        bandwidth_data['traffic_in'] = lastvalue
                        bandwidth_data['traffic_in_bps'] = lastvalue * 8  # Convert to bits
                    elif 'out[' in item['key_']:
                        bandwidth_data['traffic_out'] = lastvalue
                        bandwidth_data['traffic_out_bps'] = lastvalue * 8
                
                return bandwidth_data
            else:
                print(f"❌ Error getting bandwidth: {result.get('error', {})}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_triggers(self, hostids=None, min_severity=2):
        """Ambil trigger/alert dari Zabbix"""
        if not self.token:
            self.authenticate()
        
        params = {
            "output": ["triggerid", "description", "priority", "lastchange", "value"],
            "selectHosts": ["hostid", "host", "name"],
            "filter": {
                "value": 1  # Only problem triggers
            },
            "min_severity": min_severity,
            "sortfield": "priority",
            "sortorder": "DESC"
        }
        
        if hostids:
            params["hostids"] = hostids
        
        payload = {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": params,
            "auth": self.token,
            "id": 5
        }
        
        try:
            response = requests.post(self.url, json=payload)
            result = response.json()
            
            if 'result' in result:
                return result['result']
            else:
                print(f"❌ Error getting triggers: {result.get('error', {})}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []


def format_bytes(bytes_value):
    """Format bytes menjadi human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_bps(bps_value):
    """Format bits per second menjadi human readable format"""
    for unit in ['bps', 'Kbps', 'Mbps', 'Gbps']:
        if bps_value < 1000.0:
            return f"{bps_value:.2f} {unit}"
        bps_value /= 1000.0
    return f"{bps_value:.2f} Tbps"
