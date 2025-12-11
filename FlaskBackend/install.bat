@echo off
REM Installation script for NMS System (Windows)
REM This script will help you set up the NMS system

echo ======================================
echo NMS System - Installation Script
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo.

REM Navigate to backend directory
cd FlaskBackend

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo Dependencies installed successfully
) else (
    echo Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Setup .env file
echo Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit .env file with your configuration
) else (
    echo .env file already exists
)
echo.

REM Database setup prompt
echo ======================================
echo Database Setup
echo ======================================
set /p DB_SETUP="Do you want to setup the database now? (y/n): "
if /i "%DB_SETUP%"=="y" (
    echo.
    set /p MYSQL_USER="MySQL username (default: root): "
    if "%MYSQL_USER%"=="" set MYSQL_USER=root
    
    set /p MYSQL_PASS="MySQL password: "
    
    echo Creating database and tables...
    mysql -u %MYSQL_USER% -p%MYSQL_PASS% < database_schema.sql
    
    if %errorlevel% equ 0 (
        echo Database setup completed
    ) else (
        echo Database setup failed
        echo Please check your MySQL credentials and try again
    )
)
echo.

REM Test connections
echo ======================================
echo Test Connections
echo ======================================
set /p TEST_CONN="Do you want to test connections now? (y/n): "
if /i "%TEST_CONN%"=="y" (
    echo.
    python test_connections.py
)
echo.

REM Installation complete
echo ======================================
echo Installation Complete!
echo ======================================
echo.
echo Next Steps:
echo 1. Edit .env file with your configuration:
echo    notepad .env
echo.
echo 2. Start the application:
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 3. Access the API at:
echo    http://localhost:5000
echo.
echo For more information, see:
echo    - README.md
echo    - QUICKSTART.md
echo    - API_DOCUMENTATION.md
echo.
echo Happy Monitoring!
echo.

pause
