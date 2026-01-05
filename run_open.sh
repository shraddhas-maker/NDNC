#!/bin/bash

echo ""
echo "============================================================"
echo "🔄 NDNC Open Complaints Workflow"
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

# Run automation with option 2 (Open)
echo "2" | python3 complete_ndnc_automation.py

