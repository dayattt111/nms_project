from flask import Blueprint, jsonify, request
from db import get_db_connection
from datetime import datetime, timedelta
from service.network_service import (
    get_interface_bandwidth, 
    get_interface_info, 
    get_wifi_clients,
    get_signal_strength,
    scan_network
)
import os

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get all devices with optional filtering"""
    device_type = request.args.get('type')
    status = request.args.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM devices WHERE 1=1"
    params = []
    
    if device_type:
        query += " AND device_type=%s"
        params.append(device_type)
    
    if status:
        query += " AND status=%s"
        params.append(status)
    
    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)


@devices_bp.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get single device details"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices WHERE id=%s", (device_id,))
    device = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if device:
        return jsonify(device)
    else:
        return jsonify({"error": "Device not found"}), 404


@devices_bp.route('/devices', methods=['POST'])
def add_device():
    """Add new device"""
    data = request.json
    
    required_fields = ['name', 'ip_address']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO devices (name, ip_address, device_type, location, description, vendor, model, snmp_community)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'],
            data['ip_address'],
            data.get('device_type', 'router'),
            data.get('location', ''),
            data.get('description', ''),
            data.get('vendor', ''),
            data.get('model', ''),
            data.get('snmp_community', 'public')
        ))
        
        conn.commit()
        device_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Device added successfully",
            "device_id": device_id
        }), 201
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": str(e)}), 500


@devices_bp.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build update query dynamically
        fields = []
        values = []
        
        updateable_fields = ['name', 'ip_address', 'device_type', 'location', 'description', 'vendor', 'model', 'snmp_community']
        
        for field in updateable_fields:
            if field in data:
                fields.append(f"{field}=%s")
                values.append(data[field])
        
        if not fields:
            return jsonify({"error": "No fields to update"}), 400
        
        values.append(device_id)
        query = f"UPDATE devices SET {', '.join(fields)} WHERE id=%s"
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Device updated successfully"
        })
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": str(e)}), 500


@devices_bp.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete device"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM devices WHERE id=%s", (device_id,))
    conn.commit()
    
    if cursor.rowcount > 0:
        cursor.close()
        conn.close()
        return jsonify({
            "success": True,
            "message": "Device deleted successfully"
        })
    else:
        cursor.close()
        conn.close()
        return jsonify({"error": "Device not found"}), 404


@devices_bp.route('/devices/<int:device_id>/bandwidth', methods=['GET'])
def get_device_bandwidth(device_id):
    """Get real-time bandwidth for device"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices WHERE id=%s", (device_id,))
    device = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    community = device.get('snmp_community', 'public')
    interface_index = device.get('interface_index', 2)
    
    bandwidth_data = get_interface_bandwidth(device['ip_address'], community, interface_index)
    
    if bandwidth_data:
        # Save to history
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bandwidth_history 
            (device_id, interface_index, in_bytes_per_sec, out_bytes_per_sec, in_mbps, out_mbps, total_mbps, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            device_id,
            interface_index,
            bandwidth_data['in_bytes_per_sec'],
            bandwidth_data['out_bytes_per_sec'],
            bandwidth_data['in_mbps'],
            bandwidth_data['out_mbps'],
            bandwidth_data['total_mbps'],
            datetime.now()
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
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


@devices_bp.route('/devices/<int:device_id>/interfaces', methods=['GET'])
def get_device_interfaces(device_id):
    """Get list of interfaces for device"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices WHERE id=%s", (device_id,))
    device = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    community = device.get('snmp_community', 'public')
    interfaces = get_interface_info(device['ip_address'], community)
    
    return jsonify({
        "success": True,
        "device": device,
        "interfaces": interfaces
    })


@devices_bp.route('/network/scan', methods=['POST'])
def scan_network_range():
    """Scan network range for active devices"""
    data = request.json
    network_range = data.get('network_range', '192.168.1.0/24')
    
    active_devices = scan_network(network_range)
    
    return jsonify({
        "success": True,
        "network_range": network_range,
        "found_devices": len(active_devices),
        "devices": active_devices
    })
