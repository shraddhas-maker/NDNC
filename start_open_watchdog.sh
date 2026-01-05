#!/bin/bash

echo ""
echo "============================================================"
echo "🔍 NDNC Open Folder Watchdog"
echo "============================================================"
echo ""

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the watchdog
python3 watch_open_folder.py

