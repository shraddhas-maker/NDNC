#!/bin/bash

echo ""
echo "========================================================================"
echo "🤖 NDNC Complete Automation - All Workflows"
echo "========================================================================"
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

echo "This will run:"
echo "  1. Review Pending: Download from dashboard + verify"
echo "  2. Open: Process existing files from open/ folder"
echo "  3. Watchdog: Monitor open/ folder for new files"
echo ""
echo "Starting in 2 seconds..."
sleep 2

echo ""
echo "========================================================================"
echo "STEP 1: Processing Review Pending Complaints"
echo "========================================================================"
echo ""
echo "→ This will download files from dashboard and verify them"
echo ""

# Run Review Pending workflow
python3 complete_ndnc_automation.py review_pending

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Review Pending workflow had issues, but continuing..."
    echo ""
fi

echo ""
echo "========================================================================"
echo "STEP 2: Processing Open Complaints (Existing Files)"
echo "========================================================================"
echo ""
echo "→ This will process files already in open/ folder"
echo ""

# Run Open workflow
python3 complete_ndnc_automation.py open

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Open workflow had issues, but continuing to watchdog..."
    echo ""
fi

echo ""
echo "========================================================================"
echo "STEP 3: Starting Open Folder Watchdog"
echo "========================================================================"
echo ""
echo "→ Monitoring: /Users/shraddha.s/Downloads/NDNC/open/"
echo "→ Drop PDF/PNG files to auto-process"
echo "→ Press Ctrl+C to stop"
echo ""

# Start watchdog (runs continuously)
python3 watch_open_folder.py

echo ""
echo "✓ All workflows completed!"
echo ""

