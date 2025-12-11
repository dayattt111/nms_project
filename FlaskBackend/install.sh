#!/bin/bash

# Installation script for NMS System
# This script will help you set up the NMS system

echo "======================================"
echo "NMS System - Installation Script"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Please do not run this script as root"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION installed"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Check MySQL
echo ""
echo "🔍 Checking MySQL..."
if command -v mysql &> /dev/null; then
    echo "✅ MySQL installed"
else
    echo "⚠️  MySQL not found. Please install MySQL or MariaDB"
    echo "   Ubuntu/Debian: sudo apt-get install mysql-server"
    echo "   CentOS/RHEL: sudo yum install mysql-server"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
cd FlaskBackend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Setup .env file
echo ""
echo "📝 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "ℹ️  .env file already exists"
fi

# Setup database
echo ""
echo "🗄️  Database Setup"
echo "-----------------------------------"
read -p "Do you want to setup the database now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "MySQL root password: " -s MYSQL_PASSWORD
    echo ""
    
    echo "Creating database and tables..."
    mysql -u root -p"$MYSQL_PASSWORD" < database_schema.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Database setup completed"
    else
        echo "❌ Database setup failed"
    fi
fi

# Test connections
echo ""
echo "🧪 Testing Connections"
echo "-----------------------------------"
read -p "Do you want to test connections now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python test_connections.py
fi

# Installation complete
echo ""
echo "======================================"
echo "✅ Installation Complete!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Start the application:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "3. Access the API at:"
echo "   http://localhost:5000"
echo ""
echo "📖 For more information, see:"
echo "   - README.md"
echo "   - QUICKSTART.md"
echo "   - API_DOCUMENTATION.md"
echo ""
echo "Happy Monitoring! 🚀"
