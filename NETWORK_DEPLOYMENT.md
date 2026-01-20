# Network Deployment Guide

This guide explains how to deploy the NDNC Automation dashboard for network access, allowing others to control the automation from their browsers while it runs on your machine.

## 🌐 Deployment Scenarios

### Scenario 1: Same Network (WiFi/LAN) - **Recommended**
- ✅ Easy setup
- ✅ No external services needed
- ✅ Fast and secure
- ⚠️ Requires same WiFi/LAN network

### Scenario 2: Remote Access (ngrok)
- ✅ Works from anywhere
- ✅ No router configuration
- ⚠️ Requires ngrok account (free tier available)
- ⚠️ URLs change on each restart (free tier)

---

## 📋 Prerequisites

1. **Your PC (Server Host)**
   - Python 3.8+ installed
   - Chrome browser installed
   - Node.js 18+ installed (for rebuilding frontend)
   - Repository cloned

2. **Other Users**
   - Web browser (Chrome, Firefox, Safari, Edge)
   - Same network (for Scenario 1) or internet (for Scenario 2)

---

## 🚀 Quick Setup (Same Network)

### Step 1: Find Your Local IP Address

Run the helper script:
```bash
./get_local_ip.sh
```

This will display your IP address (e.g., `192.168.1.100`). Copy it!

**Manual Method:**
- **macOS:** `ifconfig | grep "inet " | grep -v 127.0.0.1`
- **Linux:** `ip addr show | grep "inet " | grep -v 127.0.0.1`
- **Windows:** `ipconfig` (look for "IPv4 Address")

### Step 2: Configure Frontend

Create `.env` file in the `frontend/` directory:

```bash
cd frontend
echo 'VITE_API_URL=http://YOUR_IP:5000' > .env
# Replace YOUR_IP with your actual IP, e.g., http://192.168.1.100:5000
```

**Example:**
```bash
echo 'VITE_API_URL=http://192.168.1.100:5000' > .env
```

### Step 3: Rebuild Frontend

```bash
npm run build
cd ..
```

### Step 4: Deploy to GitHub Pages

```bash
git add frontend/.env frontend/dist
git commit -m "Configure API URL for network deployment"
git push origin main
```

Wait 1-2 minutes for GitHub Actions to deploy.

### Step 5: Start API Server

On your PC, run:
```bash
./start_api_server.sh
```

Keep this terminal open and your PC running!

### Step 6: Share Dashboard URL

Give others this URL:
```
https://YOUR_GITHUB_USERNAME.github.io/NDNC/
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

---

## 🌍 Remote Access Setup (Using ngrok)

### Step 1: Install ngrok

**macOS (Homebrew):**
```bash
brew install ngrok
```

**Linux/Windows:**
Download from https://ngrok.com/download

### Step 2: Sign Up and Authenticate

1. Create free account at https://ngrok.com/
2. Get your authtoken from dashboard
3. Authenticate:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Start API Server

```bash
./start_api_server.sh
```

### Step 4: Start ngrok Tunnel (in a new terminal)

```bash
ngrok http 5000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

Copy the `https://abc123.ngrok.io` URL!

### Step 5: Update Frontend Configuration

```bash
cd frontend
echo 'VITE_API_URL=https://abc123.ngrok.io' > .env
npm run build
cd ..
git add frontend/.env frontend/dist
git commit -m "Configure API URL for ngrok deployment"
git push origin main
```

### Step 6: Share Dashboard URL

Share: `https://YOUR_GITHUB_USERNAME.github.io/NDNC/`

⚠️ **Note:** With free ngrok, the URL changes each time you restart ngrok, so you'll need to update and redeploy the frontend each time.

---

## 🔒 Security Considerations

### Current Setup (No Authentication)
- ⚠️ Anyone with the URL can control your automation
- ⚠️ No password or login required
- ✅ Suitable for trusted team members on private network

### Recommendations:
1. **Network Firewall:** Ensure port 5000 is blocked from external access (use same-network setup)
2. **VPN:** Use company VPN for remote access instead of ngrok
3. **IP Whitelist:** Configure firewall to allow only specific IP addresses
4. **Add Authentication:** (Future enhancement - can be implemented if needed)

---

## 🖥️ How It Works

```
┌─────────────────────┐         ┌─────────────────────┐
│  Other User's       │         │   Your PC           │
│  Browser            │  HTTP   │                     │
│  (GitHub Pages)     │◄───────►│  API Server         │
│                     │ Port    │  (Flask/SocketIO)   │
│  React Frontend     │  5000   │                     │
└─────────────────────┘         │  ↓                  │
                                 │  Python Automation  │
                                 │  Chrome Browser     │
                                 │  Selenium           │
                                 └─────────────────────┘
```

### Key Points:
- **Frontend:** Hosted on GitHub Pages (static files)
- **API Server:** Runs on your PC (Flask application)
- **Automation:** Executes on your PC (Selenium + Chrome)
- **Control:** Users trigger actions via frontend
- **Execution:** All processing happens on your machine

---

## ⚡ Quick Commands Reference

### Get Your IP
```bash
./get_local_ip.sh
```

### Configure Frontend (Local Network)
```bash
cd frontend
echo 'VITE_API_URL=http://192.168.1.100:5000' > .env
npm run build
```

### Configure Frontend (ngrok)
```bash
cd frontend
echo 'VITE_API_URL=https://abc123.ngrok.io' > .env
npm run build
```

### Deploy Changes
```bash
git add frontend/.env frontend/dist
git commit -m "Update API configuration"
git push origin main
```

### Start Server
```bash
./start_api_server.sh
```

### Start ngrok (if using remote access)
```bash
ngrok http 5000
```

---

## 🐛 Troubleshooting

### "Failed to fetch" Error in Frontend

**Cause:** Frontend can't reach API server

**Solutions:**
1. Verify server is running: `./start_api_server.sh`
2. Check IP address in `.env` is correct
3. Verify port 5000 is not blocked by firewall
4. Ensure users are on same network (local deployment)
5. Check ngrok tunnel is active (remote deployment)

### "Connection refused" Error

**Cause:** API server not accessible

**Solutions:**
1. Verify server is running on port 5000
2. Check firewall settings: `sudo lsof -i :5000`
3. Try accessing from your own browser: `http://YOUR_IP:5000/api/status`

### Changes Not Reflecting

**Cause:** Old build cached

**Solutions:**
1. Clear browser cache
2. Rebuild frontend: `cd frontend && npm run build`
3. Wait for GitHub Actions to complete deployment
4. Hard refresh browser: `Ctrl+F5` or `Cmd+Shift+R`

### ngrok URL Changes

**Cause:** Free ngrok URLs are temporary

**Solutions:**
1. Use paid ngrok plan for permanent URLs
2. Update frontend `.env` with new URL each time
3. Consider same-network deployment instead

---

## 📊 Testing Your Setup

### 1. Test API Server Locally
```bash
curl http://localhost:5000/api/status
```

Should return JSON with status information.

### 2. Test API Server from Network
From another device on same network:
```bash
curl http://YOUR_IP:5000/api/status
```

### 3. Test Frontend Connection
Open the dashboard URL in browser, check console for connection messages.

---

## 🔄 Switching Back to Local-Only

To revert to local-only mode:

```bash
cd frontend
rm .env
npm run build
cd ..
git add frontend
git commit -m "Revert to local-only mode"
git push origin main
```

The frontend will default back to `http://localhost:5000`.

---

## 💡 Best Practices

1. **Keep Server Running:** Don't sleep/shutdown your PC while others are using it
2. **Monitor Logs:** Watch the terminal for real-time processing status
3. **Stable Network:** Use wired Ethernet for better reliability
4. **Firewall Rules:** Only open port 5000, keep everything else blocked
5. **VPN Over ngrok:** Use company VPN instead of ngrok for corporate use
6. **Regular Updates:** Keep the repository and dependencies updated

---

## 📞 Support

If you encounter issues:
1. Check this guide's Troubleshooting section
2. Verify all prerequisites are installed
3. Test each component individually
4. Check firewall and network settings
5. Review API server logs for errors

---

## 🎯 Next Steps

Once deployed:
- ✅ Users can access the dashboard from their browsers
- ✅ Click buttons to trigger Review Pending or Open workflows
- ✅ See real-time logs and status updates
- ✅ Pause, resume, or stop automation as needed
- ⚠️ Remember: All processing happens on YOUR machine!

