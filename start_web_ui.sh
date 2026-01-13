#!/bin/bash

# NDNC Automation Web UI Startup Script

echo "🚀 Starting NDNC Automation Web UI..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip3 install -r requirements.txt
    echo ""
fi

# Start the web server
echo "🌐 Starting web server on http://localhost:5000"
echo "🎯 Open your browser and navigate to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 web_ui.py

