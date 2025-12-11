from ping3 import ping
from db import get_db_connection
from datetime import datetime
from pysnmp.hlapi import *
import time

def check_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()

    for device in devices:
        response = ping(device['ip_address'], timeout=2)
        status = 'up' if response else 'down'

        cursor.execute("""
            UPDATE devices SET status=%s, last_checked=%s WHERE id=%s
        """, (status, datetime.now(), device['id']))
        conn.commit()

    cursor.close()
    conn.close()


def get_interface_bandwidth(ip, community='public', interface_index=2):
    """
    Mengambil data bandwidth interface menggunakan SNMP
    interface_index: 1=lo, 2=eth0, dll (sesuaikan dengan perangkat)
    """
    # OID untuk traffic counter
    oid_in = f'1.3.6.1.2.1.2.2.1.10.{interface_index}'   # ifInOctets
    oid_out = f'1.3.6.1.2.1.2.2.1.16.{interface_index}'  # ifOutOctets
    
    try:
        # Ambil nilai pertama
        in_octets_1 = get_snmp_value(ip, community, oid_in)
        out_octets_1 = get_snmp_value(ip, community, oid_out)
        
        if in_octets_1 is None or out_octets_1 is None:
            return None
        
        # Tunggu 1 detik
        time.sleep(1)
        
        # Ambil nilai kedua
        in_octets_2 = get_snmp_value(ip, community, oid_in)
        out_octets_2 = get_snmp_value(ip, community, oid_out)
        
        if in_octets_2 is None or out_octets_2 is None:
            return None
        
        # Hitung bandwidth (bytes per second)
        in_bps = (in_octets_2 - in_octets_1)
        out_bps = (out_octets_2 - out_octets_1)
        
        # Convert ke Mbps
        in_mbps = (in_bps * 8) / (1024 * 1024)
        out_mbps = (out_bps * 8) / (1024 * 1024)
        
        return {
            'ip': ip,
            'interface_index': interface_index,
            'in_bytes_per_sec': in_bps,
            'out_bytes_per_sec': out_bps,
            'in_mbps': round(in_mbps, 2),
            'out_mbps': round(out_mbps, 2),
            'total_mbps': round(in_mbps + out_mbps, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting bandwidth for {ip}: {e}")
        return None


def get_snmp_value(ip, community, oid):
    """Helper function untuk mendapatkan nilai SNMP"""
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"SNMP error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"SNMP error: {errorStatus.prettyPrint()}")
            return None
        else:
            for varBind in varBinds:
                return int(varBind[1])
    except Exception as e:
        print(f"Error SNMP {ip}: {e}")
        return None


def get_interface_info(ip, community='public'):
    """Mendapatkan daftar interface yang tersedia"""
    interfaces = []
    
    # OID untuk interface description dan status
    base_oid_desc = '1.3.6.1.2.1.2.2.1.2'    # ifDescr
    base_oid_status = '1.3.6.1.2.1.2.2.1.8'  # ifOperStatus
    
    try:
        # Scan interface 1-10 (bisa disesuaikan)
        for i in range(1, 11):
            desc = get_snmp_string(ip, community, f'{base_oid_desc}.{i}')
            status = get_snmp_value(ip, community, f'{base_oid_status}.{i}')
            
            if desc and status:
                interfaces.append({
                    'index': i,
                    'description': desc,
                    'status': 'up' if status == 1 else 'down'
                })
        
        return interfaces
    except Exception as e:
        print(f"❌ Error getting interfaces for {ip}: {e}")
        return []


def get_snmp_string(ip, community, oid):
    """Helper function untuk mendapatkan string dari SNMP"""
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication or errorStatus:
            return None
        else:
            for varBind in varBinds:
                return str(varBind[1])
    except Exception as e:
        return None
