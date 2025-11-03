from ping3 import ping
from db import get_db_connection
from datetime import datetime

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
