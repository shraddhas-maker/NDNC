#!/bin/bash
# Script to get local IP address for network deployment

echo "========================================"
echo "🌐 NDNC Automation - Network IP Finder"
echo "========================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📍 Detected: macOS"
    echo ""
    echo "Your local IP addresses:"
    echo "------------------------"
    ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print "   → " $2}'
    
    # Get the most likely IP (first non-localhost)
    PRIMARY_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}')
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "📍 Detected: Linux"
    echo ""
    echo "Your local IP addresses:"
    echo "------------------------"
    ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print "   → " $2}' | cut -d'/' -f1
    
    # Get the most likely IP
    PRIMARY_IP=$(ip addr show | grep "inet " | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}' | cut -d'/' -f1)
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash or Cygwin)
    echo "📍 Detected: Windows"
    echo ""
    echo "Your local IP addresses:"
    echo "------------------------"
    ipconfig | grep "IPv4" | awk '{print "   → " $NF}'
    
    # Get the most likely IP
    PRIMARY_IP=$(ipconfig | grep "IPv4" | head -n 1 | awk '{print $NF}')
else
    echo "❌ Unknown OS: $OSTYPE"
    echo "Please manually find your IP address"
    exit 1
fi

echo ""
echo "========================================"
echo "📋 Setup Instructions"
echo "========================================"
echo ""

if [ -n "$PRIMARY_IP" ]; then
    echo "✅ Recommended IP: $PRIMARY_IP"
    echo ""
    echo "To deploy for network access:"
    echo ""
    echo "1️⃣  Create frontend/.env file:"
    echo "   cd frontend"
    echo "   echo 'VITE_API_URL=http://$PRIMARY_IP:5000' > .env"
    echo ""
    echo "2️⃣  Rebuild frontend:"
    echo "   npm run build"
    echo ""
    echo "3️⃣  Deploy to GitHub Pages:"
    echo "   cd .."
    echo "   git add frontend/.env frontend/dist"
    echo "   git commit -m 'Update API URL for network deployment'"
    echo "   git push origin main"
    echo ""
    echo "4️⃣  Start the API server:"
    echo "   ./start_api_server.sh"
    echo ""
    echo "5️⃣  Share the dashboard URL with others:"
    echo "   https://YOUR_GITHUB_USERNAME.github.io/NDNC/"
    echo ""
    echo "⚠️  Important:"
    echo "   • Keep your PC on and server running"
    echo "   • Ensure port 5000 is not blocked by firewall"
    echo "   • Users must be on the same network (WiFi/LAN)"
else
    echo "⚠️  Could not automatically determine IP"
    echo "Please run 'ifconfig' (Mac/Linux) or 'ipconfig' (Windows)"
fi

echo ""
echo "========================================"

