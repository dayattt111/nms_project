from flask import Blueprint, jsonify, request
from db import get_db_connection

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/devices', methods=['GET'])
def get_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
