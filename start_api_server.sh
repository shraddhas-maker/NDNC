#!/bin/bash

# NDNC Automation API Server Startup Script
# This starts the Flask API backend that the React frontend connects to

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=" 
echo "🚀 Starting NDNC Automation API Server"
echo "="

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment."
    exit 1
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$SCRIPT_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    deactivate
    exit 1
fi

# Check for required system dependencies
echo "🔍 Checking system dependencies..."

if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found!"
    echo "📝 Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)"
    echo ""
fi

# Start the API server
echo "=" 
echo "✅ Starting API Server on http://localhost:5000"
echo "🔌 WebSocket available on ws://localhost:5000"
echo "=" 
echo "📝 Note: Keep this terminal open. The API server must be running for the frontend to work."
echo "=" 
echo ""

python "$SCRIPT_DIR/api_server.py"

# Deactivate on exit
deactivate

