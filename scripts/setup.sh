#!/bin/bash

# Setup script for VSS Complete Project
# Hướng dẫn cài đặt tự động dự án VSS

set -e

echo "🚀 VSS Complete Project - Setup Script"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14+ first."
    exit 1
fi

echo "✅ Python and Node.js are available"

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/output
mkdir -p data/backup

# Set up configuration files
echo "⚙️ Setting up configuration..."
if [ ! -f "config/.env" ]; then
    echo "Creating default .env file..."
    cat > config/.env << EOF
# VSS Configuration
VSS_BASE_URL=https://baohiemxahoi.gov.vn
VSS_TIMEOUT=30
VSS_MAX_RETRIES=3

# Proxy Configuration (optional)
# PROXY_SERVER=ip.mproxy.vn:12301
# PROXY_USER=username
# PROXY_PASS=password

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/vss.log

# Rate Limiting
REQUEST_DELAY=2
BATCH_SIZE=10
EOF
fi

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x scripts/*.sh
chmod +x examples/*.py

# Test installation
echo "🧪 Testing installation..."
python3 -c "import requests, beautifulsoup4, pandas; print('✅ Python dependencies OK')"
node -e "const axios = require('axios'); const cheerio = require('cheerio'); console.log('✅ Node.js dependencies OK')"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📚 Quick Start:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Edit configuration: config/vss_config.yaml"
echo "   3. Run basic example: python examples/basic_usage.py"
echo "   4. Process Excel file: python examples/excel_processing.py"
echo ""
echo "📖 Read README.md for detailed usage instructions"
echo ""
