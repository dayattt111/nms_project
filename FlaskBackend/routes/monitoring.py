from flask import Blueprint, jsonify, request
from db import get_db_connection
from service.network_service import get_interface_bandwidth, get_interface_info
from service.zabbix_service import ZabbixAPI, format_bytes, format_bps
from service.telegram_service import send_bandwidth_alert, send_bandwidth_low_alert
import os

monitoring_bp = Blueprint('monitoring', __name__)

# Initialize Zabbix API
zabbix = ZabbixAPI()


@monitoring_bp.route('/monitoring/bandwidth/<device_id>', methods=['GET'])
def get_device_bandwidth(device_id):
    """Mendapatkan bandwidth real-time dari device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE id=%s", (device_id,))
        device = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not device:
            return jsonify({"error": "Device not found"}), 404
        
        ip = device['ip_address']
        community = os.getenv('SNMP_COMMUNITY', 'public')
        interface_index = request.args.get('interface', 2, type=int)
        
        bandwidth_data = get_interface_bandwidth(ip, community, interface_index)
        
        if bandwidth_data:
            return jsonify({
                "success": True,
                "device": device,
                "bandwidth": bandwidth_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not retrieve bandwidth data"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/monitoring/interfaces/<device_id>', methods=['GET'])
def get_device_interfaces(device_id):
    """Mendapatkan daftar interface dari device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE id=%s", (device_id,))
        device = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not device:
            return jsonify({"error": "Device not found"}), 404
        
        ip = device['ip_address']
        community = os.getenv('SNMP_COMMUNITY', 'public')
        
        interfaces = get_interface_info(ip, community)
        
        return jsonify({
            "success": True,
            "device": device,
            "interfaces": interfaces
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/monitoring/bandwidth/all', methods=['GET'])
def get_all_bandwidth():
    """Mendapatkan bandwidth dari semua device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE status='up'")
        devices = cursor.fetchall()
        cursor.close()
        conn.close()
        
        results = []
        community = os.getenv('SNMP_COMMUNITY', 'public')
        
        for device in devices:
            bandwidth_data = get_interface_bandwidth(device['ip_address'], community)
            if bandwidth_data:
                results.append({
                    "device": device,
                    "bandwidth": bandwidth_data
                })
        
        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/zabbix/hosts', methods=['GET'])
def get_zabbix_hosts():
    """Mendapatkan daftar host dari Zabbix"""
    try:
        hosts = zabbix.get_hosts()
        return jsonify({
            "success": True,
            "count": len(hosts),
            "hosts": hosts
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/zabbix/host/<hostid>/items', methods=['GET'])
def get_zabbix_host_items(hostid):
    """Mendapatkan items dari host Zabbix"""
    try:
        items = zabbix.get_host_items(hostid)
        return jsonify({
            "success": True,
            "hostid": hostid,
            "count": len(items),
            "items": items
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/zabbix/host/<hostid>/bandwidth', methods=['GET'])
def get_zabbix_bandwidth(hostid):
    """Mendapatkan data bandwidth dari Zabbix"""
    try:
        interface = request.args.get('interface', 'eth0')
        bandwidth_data = zabbix.get_bandwidth_data(hostid, interface)
        
        if bandwidth_data:
            # Format data untuk display
            bandwidth_data['traffic_in_formatted'] = format_bytes(bandwidth_data['traffic_in'])
            bandwidth_data['traffic_out_formatted'] = format_bytes(bandwidth_data['traffic_out'])
            bandwidth_data['traffic_in_bps_formatted'] = format_bps(bandwidth_data['traffic_in_bps'])
            bandwidth_data['traffic_out_bps_formatted'] = format_bps(bandwidth_data['traffic_out_bps'])
            
            return jsonify({
                "success": True,
                "data": bandwidth_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not retrieve bandwidth data"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/zabbix/triggers', methods=['GET'])
def get_zabbix_triggers():
    """Mendapatkan trigger/alert dari Zabbix"""
    try:
        min_severity = request.args.get('severity', 2, type=int)
        triggers = zabbix.get_triggers(min_severity=min_severity)
        
        return jsonify({
            "success": True,
            "count": len(triggers),
            "triggers": triggers
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/monitoring/check-bandwidth', methods=['POST'])
def check_bandwidth_threshold():
    """Cek bandwidth dan kirim alert jika melebihi threshold"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        threshold_high = data.get('threshold_high', 80)  # Mbps
        threshold_low = data.get('threshold_low', 1)     # Mbps
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE id=%s", (device_id,))
        device = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not device:
            return jsonify({"error": "Device not found"}), 404
        
        community = os.getenv('SNMP_COMMUNITY', 'public')
        bandwidth_data = get_interface_bandwidth(device['ip_address'], community)
        
        if not bandwidth_data:
            return jsonify({"error": "Could not get bandwidth data"}), 500
        
        alerts_sent = []
        
        # Check high bandwidth
        if bandwidth_data['total_mbps'] > threshold_high:
            send_bandwidth_alert(
                device['name'], 
                device['ip_address'], 
                bandwidth_data, 
                threshold_high
            )
            alerts_sent.append('high_bandwidth_alert')
        
        # Check low bandwidth
        if bandwidth_data['total_mbps'] < threshold_low and bandwidth_data['total_mbps'] > 0:
            send_bandwidth_low_alert(
                device['name'], 
                device['ip_address'], 
                bandwidth_data, 
                threshold_low
            )
            alerts_sent.append('low_bandwidth_alert')
        
        return jsonify({
            "success": True,
            "device": device,
            "bandwidth": bandwidth_data,
            "alerts_sent": alerts_sent
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/monitoring/sync-zabbix', methods=['POST'])
def sync_zabbix_to_db():
    """Sinkronisasi host dari Zabbix ke database lokal"""
    try:
        hosts = zabbix.get_hosts()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        synced = 0
        for host in hosts:
            # Get IP from interfaces
            ip = 'N/A'
            if host.get('interfaces') and len(host['interfaces']) > 0:
                ip = host['interfaces'][0].get('ip', 'N/A')
            
            # Check if device exists
            cursor.execute("SELECT id FROM devices WHERE ip_address=%s", (ip,))
            existing = cursor.fetchone()
            
            if not existing and ip != 'N/A':
                # Insert new device
                cursor.execute("""
                    INSERT INTO devices (name, ip_address, status, device_type, zabbix_hostid) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    host['name'], 
                    ip, 
                    'up' if host['status'] == '0' else 'down',
                    'router',
                    host['hostid']
                ))
                synced += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Synced {synced} hosts from Zabbix",
            "total_hosts": len(hosts)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
