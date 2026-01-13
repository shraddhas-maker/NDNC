#!/bin/bash

echo ""
echo "========================================================================"
echo "🔄 Process Review Pending Files (No Download)"
echo "========================================================================"
echo ""
echo "This will process files already in review_pending/ folder"
echo "No dashboard download - just search, verify, move to processed_review/"
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

# Run processor
python3 process_review_pending_only.py

