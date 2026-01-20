#!/bin/bash
# Helper script to set up ngrok tunnel for remote access

echo "========================================"
echo "🌍 NDNC Automation - ngrok Setup"
echo "========================================"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed!"
    echo ""
    echo "To install ngrok:"
    echo "  • macOS: brew install ngrok"
    echo "  • Linux/Windows: Download from https://ngrok.com/download"
    echo ""
    echo "After installation:"
    echo "  1. Sign up at https://ngrok.com/"
    echo "  2. Get your authtoken from dashboard"
    echo "  3. Run: ngrok config add-authtoken YOUR_AUTH_TOKEN"
    echo "  4. Run this script again"
    exit 1
fi

echo "✅ ngrok is installed"
echo ""
echo "📋 Instructions:"
echo ""
echo "1️⃣  Start your API server (in another terminal):"
echo "   ./start_api_server.sh"
echo ""
echo "2️⃣  Press ENTER to start ngrok tunnel..."
read -p ""

echo ""
echo "🚀 Starting ngrok tunnel on port 5000..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  IMPORTANT:"
echo "   1. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)"
echo "   2. Stop this script (Ctrl+C) when done"
echo "   3. Update frontend/.env with the copied URL:"
echo "      VITE_API_URL=https://abc123.ngrok.io"
echo "   4. Rebuild and deploy:"
echo "      cd frontend && npm run build && cd .."
echo "      git add frontend && git commit -m 'Update ngrok URL'"
echo "      git push origin main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting ngrok in 3 seconds..."
sleep 3

# Start ngrok
ngrok http 5000

