-- Database Schema untuk Network Monitoring System (NMS)

CREATE DATABASE IF NOT EXISTS nms_dcc;
USE nms_dcc;

-- Table untuk menyimpan device/perangkat yang dimonitor
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ip_address VARCHAR(50) NOT NULL UNIQUE,
    device_type ENUM('router', 'switch', 'server', 'firewall', 'other') DEFAULT 'router',
    status ENUM('up', 'down', 'unknown') DEFAULT 'unknown',
    last_checked DATETIME,
    zabbix_hostid VARCHAR(50),
    snmp_community VARCHAR(50) DEFAULT 'public',
    interface_index INT DEFAULT 2,
    location VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ip (ip_address),
    INDEX idx_status (status),
    INDEX idx_zabbix (zabbix_hostid)
);

-- Table untuk menyimpan history bandwidth
CREATE TABLE IF NOT EXISTS bandwidth_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    interface_index INT DEFAULT 2,
    in_bytes_per_sec BIGINT DEFAULT 0,
    out_bytes_per_sec BIGINT DEFAULT 0,
    in_mbps DECIMAL(10, 2) DEFAULT 0,
    out_mbps DECIMAL(10, 2) DEFAULT 0,
    total_mbps DECIMAL(10, 2) DEFAULT 0,
    timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_time (device_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- Table untuk menyimpan alert history
CREATE TABLE IF NOT EXISTS alert_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    alert_type ENUM('device_down', 'device_up', 'bandwidth_high', 'bandwidth_low', 'zabbix_trigger') NOT NULL,
    severity ENUM('info', 'warning', 'critical') DEFAULT 'warning',
    message TEXT NOT NULL,
    alert_data JSON,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL,
    INDEX idx_device (device_id),
    INDEX idx_type (alert_type),
    INDEX idx_created (created_at)
);

-- Table untuk menyimpan Zabbix trigger yang sudah diproses
CREATE TABLE IF NOT EXISTS zabbix_triggers_processed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trigger_id VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    priority INT,
    last_processed DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trigger (trigger_id),
    INDEX idx_last_processed (last_processed)
);

-- Table untuk konfigurasi threshold per device
CREATE TABLE IF NOT EXISTS device_thresholds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    bandwidth_high_mbps DECIMAL(10, 2) DEFAULT 80,
    bandwidth_low_mbps DECIMAL(10, 2) DEFAULT 1,
    ping_timeout INT DEFAULT 2,
    check_interval INT DEFAULT 60,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    UNIQUE KEY unique_device (device_id)
);

-- Insert sample data
INSERT INTO devices (name, ip_address, device_type, status, location, description) VALUES
('Router Utama', '192.168.1.1', 'router', 'unknown', 'Data Center', 'Router utama untuk koneksi internet'),
('Switch Core', '192.168.1.2', 'switch', 'unknown', 'Data Center', 'Switch core untuk jaringan internal'),
('Server Web', '192.168.1.10', 'server', 'unknown', 'Server Room', 'Web server production');

-- Insert default thresholds
INSERT INTO device_thresholds (device_id, bandwidth_high_mbps, bandwidth_low_mbps) 
SELECT id, 80, 1 FROM devices;

-- View untuk monitoring summary
CREATE OR REPLACE VIEW monitoring_summary AS
SELECT 
    COUNT(*) as total_devices,
    SUM(CASE WHEN status = 'up' THEN 1 ELSE 0 END) as up_devices,
    SUM(CASE WHEN status = 'down' THEN 1 ELSE 0 END) as down_devices,
    SUM(CASE WHEN status = 'unknown' THEN 1 ELSE 0 END) as unknown_devices
FROM devices;

-- View untuk recent alerts
CREATE OR REPLACE VIEW recent_alerts AS
SELECT 
    ah.id,
    ah.alert_type,
    ah.severity,
    ah.message,
    d.name as device_name,
    d.ip_address,
    ah.created_at
FROM alert_history ah
LEFT JOIN devices d ON ah.device_id = d.id
ORDER BY ah.created_at DESC
LIMIT 100;

-- View untuk bandwidth statistics
CREATE OR REPLACE VIEW bandwidth_stats AS
SELECT 
    d.id as device_id,
    d.name as device_name,
    d.ip_address,
    AVG(bh.total_mbps) as avg_mbps,
    MAX(bh.total_mbps) as max_mbps,
    MIN(bh.total_mbps) as min_mbps,
    COUNT(*) as total_records,
    MAX(bh.timestamp) as last_recorded
FROM devices d
LEFT JOIN bandwidth_history bh ON d.id = bh.device_id
WHERE bh.timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY d.id, d.name, d.ip_address;
