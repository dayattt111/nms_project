@echo off
REM Quick setup for fake routers on Windows

echo ==========================================
echo Starting NMS Fake Router Quick Setup
echo ==========================================
echo.

REM Check if in correct directory
if not exist "fake_multiple_routers.py" (
    echo Error: fake_multiple_routers.py not found
    echo Please run this script from FlaskBackend directory
    pause
    exit /b 1
)

REM Check database
echo Step 1: Checking database...
mysql -u root -e "USE nms_dcc; SHOW TABLES;" >nul 2>&1
if %errorlevel% neq 0 (
    echo Database not found. Please setup database first:
    echo    mysql -u root -p ^< database_schema.sql
    pause
    exit /b 1
)
echo Database OK
echo.

REM Start fake routers
echo Step 2: Starting fake routers...
start /B python fake_multiple_routers.py > fake_routers.log 2>&1
timeout /t 3 /nobreak >nul
echo Fake routers started
echo Log: fake_routers.log
echo.

REM Add devices to database
echo Step 3: Adding devices to NMS...

mysql -u root nms_dcc -e "DELETE FROM devices WHERE ip_address='127.0.0.1';"
mysql -u root nms_dcc -e "INSERT INTO devices (name, ip_address, device_type, location, http_port, status) VALUES ('Router-Office-1', '127.0.0.1', 'router', 'Lantai 1', 8081, 'unknown'), ('Router-Office-2', '127.0.0.1', 'router', 'Lantai 2', 8082, 'unknown'), ('AP-Meeting-Room', '127.0.0.1', 'wifi_ap', 'Meeting Room', 8083, 'unknown');"
mysql -u root nms_dcc -e "SELECT * FROM devices WHERE ip_address='127.0.0.1';"

echo Devices added to NMS
echo.

REM Test fake routers
echo Step 4: Testing fake routers...
timeout /t 2 /nobreak >nul

for %%p in (8081 8082 8083) do (
    curl -s -o nul -w "Router on port %%p: %%{http_code}\n" http://localhost:%%p/wifi
)
echo.

REM Show info
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Fake Routers Running:
echo    - Router-Office-1: http://localhost:8081
echo    - Router-Office-2: http://localhost:8082
echo    - AP-Meeting-Room: http://localhost:8083
echo.
echo Next Steps:
echo 1. Start NMS application:
echo    python app.py
echo.
echo 2. Access web interfaces:
echo    http://localhost:8081 (Router 1)
echo    http://localhost:8082 (Router 2)
echo    http://localhost:8083 (AP)
echo.
echo 3. Test endpoints:
echo    curl http://localhost:8081/wifi
echo    curl http://localhost:5000/api/devices
echo.
echo Monitoring will start automatically
echo.
echo To view logs:
echo    type fake_routers.log
echo.
echo ==========================================
echo.

pause
