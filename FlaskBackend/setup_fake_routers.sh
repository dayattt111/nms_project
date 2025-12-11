#!/bin/bash

echo "=========================================="
echo "🚀 NMS Fake Router Quick Setup"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "fake_multiple_routers.py" ]; then
    echo "❌ Error: fake_multiple_routers.py not found"
    echo "Please run this script from FlaskBackend directory"
    exit 1
fi

# Check if database is set up
echo "📋 Step 1: Checking database..."
mysql -u root -p -e "USE nms_dcc; SHOW TABLES;" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Database not found. Please setup database first:"
    echo "   mysql -u root -p < database_schema.sql"
    exit 1
fi
echo "✅ Database OK"
echo ""

# Start fake routers in background
echo "📡 Step 2: Starting fake routers..."
python fake_multiple_routers.py > fake_routers.log 2>&1 &
ROUTER_PID=$!
echo "✅ Fake routers started (PID: $ROUTER_PID)"
echo "   Log: fake_routers.log"
sleep 3
echo ""

# Add devices to database
echo "📝 Step 3: Adding devices to NMS..."

mysql -u root -p nms_dcc << EOF
DELETE FROM devices WHERE ip_address='127.0.0.1';

INSERT INTO devices (name, ip_address, device_type, location, http_port, status) VALUES
('Router-Office-1', '127.0.0.1', 'router', 'Lantai 1', 8081, 'unknown'),
('Router-Office-2', '127.0.0.1', 'router', 'Lantai 2', 8082, 'unknown'),
('AP-Meeting-Room', '127.0.0.1', 'wifi_ap', 'Meeting Room', 8083, 'unknown');

SELECT * FROM devices WHERE ip_address='127.0.0.1';
EOF

echo "✅ Devices added to NMS"
echo ""

# Test fake routers
echo "🧪 Step 4: Testing fake routers..."
sleep 2

for port in 8081 8082 8083; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/wifi)
    if [ "$response" = "200" ]; then
        echo "✅ Router on port $port: OK"
    else
        echo "❌ Router on port $port: FAILED"
    fi
done
echo ""

# Show info
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📡 Fake Routers Running:"
echo "   - Router-Office-1: http://localhost:8081"
echo "   - Router-Office-2: http://localhost:8082"
echo "   - AP-Meeting-Room: http://localhost:8083"
echo ""
echo "🎯 Next Steps:"
echo "1. Start NMS application:"
echo "   python app.py"
echo ""
echo "2. Access web interfaces:"
echo "   http://localhost:8081 (Router 1)"
echo "   http://localhost:8082 (Router 2)"
echo "   http://localhost:8083 (AP)"
echo ""
echo "3. Test endpoints:"
echo "   curl http://localhost:8081/wifi"
echo "   curl http://localhost:5000/api/devices"
echo ""
echo "📊 Monitoring will start automatically"
echo ""
echo "To stop fake routers:"
echo "   kill $ROUTER_PID"
echo ""
echo "View logs:"
echo "   tail -f fake_routers.log"
echo ""
echo "=========================================="
