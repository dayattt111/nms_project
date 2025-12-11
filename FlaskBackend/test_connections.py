#!/usr/bin/env python3
"""
Test script untuk NMS System
Test koneksi ke database, SNMP, Telegram, dan Zabbix
"""

import os
import sys
from dotenv import load_dotenv
import requests
from pysnmp.hlapi import *

# Load environment variables
load_dotenv()

def test_database():
    """Test koneksi ke database"""
    print("\n🔍 Testing Database Connection...")
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "nms_dcc")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"✅ Database connected! MySQL version: {version[0]}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_snmp(ip="127.0.0.1"):
    """Test SNMP connection"""
    print(f"\n🔍 Testing SNMP Connection to {ip}...")
    try:
        
        community = os.getenv("SNMP_COMMUNITY", "public")
        oid = "1.3.6.1.2.1.1.1.0"  # sysDescr
        
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        
        if errorIndication:
            print(f"❌ SNMP failed: {errorIndication}")
            return False
        elif errorStatus:
            print(f"❌ SNMP error: {errorStatus.prettyPrint()}")
            return False
        else:
            for varBind in varBinds:
                print(f"✅ SNMP connected! System: {varBind[1]}")
            return True
    except Exception as e:
        print(f"❌ SNMP test failed: {e}")
        return False


def test_telegram():
    """Test Telegram bot"""
    print("\n🔍 Testing Telegram Bot...")
    try:
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            print("❌ Telegram credentials not configured in .env")
            return False
        
        # Test getMe
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['username']
                print(f"✅ Telegram bot connected! Bot: @{bot_name}")
                
                # Test send message
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": "🧪 Test message from NMS System!"
                }
                send_response = requests.post(send_url, data=data, timeout=5)
                
                if send_response.status_code == 200:
                    print("✅ Test message sent successfully!")
                    return True
                else:
                    print(f"⚠️ Bot connected but failed to send message: {send_response.text}")
                    return False
            else:
                print(f"❌ Invalid bot token")
                return False
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False


def test_zabbix():
    """Test Zabbix API"""
    print("\n🔍 Testing Zabbix API...")
    try:
        url = os.getenv("ZABBIX_URL", "http://localhost/zabbix/api_jsonrpc.php")
        username = os.getenv("ZABBIX_USER", "Admin")
        password = os.getenv("ZABBIX_PASSWORD", "zabbix")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": username,
                "password": password
            },
            "id": 1
        }
        
        response = requests.post(url, json=payload, timeout=5)
        result = response.json()
        
        if 'result' in result:
            token = result['result']
            print(f"✅ Zabbix connected! Auth token: {token[:20]}...")
            
            # Test get hosts
            hosts_payload = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ["hostid", "host"],
                    "limit": 5
                },
                "auth": token,
                "id": 2
            }
            
            hosts_response = requests.post(url, json=hosts_payload, timeout=5)
            hosts_result = hosts_response.json()
            
            if 'result' in hosts_result:
                hosts = hosts_result['result']
                print(f"✅ Found {len(hosts)} hosts in Zabbix")
                for host in hosts[:3]:
                    print(f"   - {host.get('host')} (ID: {host.get('hostid')})")
                return True
            else:
                print(f"⚠️ Connected but failed to get hosts: {hosts_result.get('error', {})}")
                return False
        else:
            error = result.get('error', {})
            print(f"❌ Zabbix authentication failed: {error.get('data', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Zabbix: {e}")
        print("   Make sure Zabbix server is running and URL is correct")
        return False
    except Exception as e:
        print(f"❌ Zabbix test failed: {e}")
        return False


def test_ping(host="8.8.8.8"):
    """Test ping functionality"""
    print(f"\n🔍 Testing Ping to {host}...")
    try:
        from ping3 import ping
        
        response = ping(host, timeout=2)
        
        if response:
            print(f"✅ Ping successful! Latency: {response*1000:.2f} ms")
            return True
        else:
            print(f"❌ Ping failed - host unreachable")
            return False
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 NMS System - Connection Tests")
    print("=" * 50)
    
    results = {
        "Database": test_database(),
        "Ping": test_ping(),
        "SNMP": test_snmp("127.0.0.1"),  # Test ke localhost, ganti jika perlu
        "Telegram": test_telegram(),
        "Zabbix": test_zabbix()
    }
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}: {'PASSED' if status else 'FAILED'}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
