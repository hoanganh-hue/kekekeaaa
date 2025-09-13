#!/bin/bash

# Run script for VSS Complete Project
# Script chạy dự án VSS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 VSS Complete Project - Run Script${NC}"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Function to show menu
show_menu() {
    echo ""
    echo -e "${BLUE}📋 Select an option:${NC}"
    echo "1. Run basic single CCCD lookup"
    echo "2. Run basic batch CCCD lookup"
    echo "3. Process Excel file"
    echo "4. Run tests"
    echo "5. Check system status"
    echo "6. View logs"
    echo "7. Clean up temporary files"
    echo "8. Exit"
    echo ""
}

# Function to run single lookup
run_single_lookup() {
    echo -e "${GREEN}🔍 Running single CCCD lookup...${NC}"
    python examples/basic_usage.py --mode single
}

# Function to run batch lookup
run_batch_lookup() {
    echo -e "${GREEN}🔍 Running batch CCCD lookup...${NC}"
    python examples/basic_usage.py --mode batch
}

# Function to process Excel
process_excel() {
    echo -e "${GREEN}📊 Processing Excel file...${NC}"
    
    # Check if input file exists
    if [ ! -f "data/data-input.xlsx" ]; then
        echo -e "${RED}❌ Input file not found: data/data-input.xlsx${NC}"
        echo "Please prepare your input file first."
        return 1
    fi
    
    python examples/excel_processing.py
}

# Function to run tests
run_tests() {
    echo -e "${GREEN}🧪 Running tests...${NC}"
    python -m pytest tests/ -v
}

# Function to check system status
check_status() {
    echo -e "${GREEN}📊 System Status Check${NC}"
    echo "========================"
    
    echo "🐍 Python version:"
    python --version
    
    echo "📦 Node.js version:"
    node --version
    
    echo "🔗 Internet connectivity:"
    if curl -s --max-time 5 https://google.com > /dev/null; then
        echo "✅ Connected"
    else
        echo "❌ No connection"
    fi
    
    echo "🌐 VSS website accessibility:"
    if curl -s --max-time 10 https://baohiemxahoi.gov.vn > /dev/null; then
        echo "✅ VSS website accessible"
    else
        echo "⚠️ VSS website may be down or blocked"
    fi
    
    echo "📁 Directory structure:"
    if [ -d "src" ] && [ -d "config" ] && [ -d "data" ]; then
        echo "✅ All directories present"
    else
        echo "❌ Missing directories"
    fi
    
    echo "⚙️ Configuration files:"
    if [ -f "config/vss_config.yaml" ]; then
        echo "✅ VSS config found"
    else
        echo "❌ VSS config missing"
    fi
}

# Function to view logs
view_logs() {
    echo -e "${GREEN}📋 Recent logs:${NC}"
    
    if [ -f "logs/vss.log" ]; then
        echo "=== VSS Log (last 20 lines) ==="
        tail -20 logs/vss.log
    else
        echo "No VSS log file found"
    fi
    
    if [ -f "logs/error.log" ]; then
        echo ""
        echo "=== Error Log (last 10 lines) ==="
        tail -10 logs/error.log
    fi
}

# Function to clean up
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
    
    # Remove temporary files
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.temp" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean up browser data
    rm -rf browser_data/* 2>/dev/null || true
    rm -rf screenshots/* 2>/dev/null || true
    
    echo "✅ Cleanup completed"
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            run_single_lookup
            ;;
        2)
            run_batch_lookup
            ;;
        3)
            process_excel
            ;;
        4)
            run_tests
            ;;
        5)
            check_status
            ;;
        6)
            view_logs
            ;;
        7)
            cleanup
            ;;
        8)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            break
            ;;
        *)
            echo -e "${RED}❌ Invalid option. Please try again.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
