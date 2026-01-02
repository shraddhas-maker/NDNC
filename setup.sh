#!/bin/bash

echo "============================================================"
echo "NDNC Watchdog Automation Setup"
echo "============================================================"
echo ""

cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "→ Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment and install dependencies
echo "→ Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create NDNC download directory if it doesn't exist
NDNC_DIR="/Users/shraddha.s/Downloads/NDNC"
if [ ! -d "$NDNC_DIR" ]; then
    echo "→ Creating NDNC directory..."
    mkdir -p "$NDNC_DIR"
    echo "✓ Created: $NDNC_DIR"
fi
echo ""

# Check for Tesseract and Poppler
echo "→ Checking system dependencies..."

if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract OCR found"
else
    echo "⚠️  Tesseract OCR not found. Install with: brew install tesseract"
fi

if command -v pdfinfo &> /dev/null; then
    echo "✓ Poppler found"
else
    echo "⚠️  Poppler not found. Install with: brew install poppler"
fi

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "To start the watchdog:"
echo "  ./start_watchdog.sh"
echo ""
echo "The watchdog will monitor: $NDNC_DIR"
echo "Drop PDF files there to automatically process them."
echo ""

