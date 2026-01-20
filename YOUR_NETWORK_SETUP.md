# 🌐 Your Network Deployment Configuration

## ✅ Setup Complete!

Your NDNC Automation is now configured for network access!

---

## 📍 Your Configuration

**Your Local IP Address:** `10.20.5.3`  
**API Server Port:** `5000`  
**API Endpoint:** `http://10.20.5.3:5000`

---

## 🚀 How to Use

### Step 1: Start the API Server on Your PC

```bash
cd /Users/shraddha.s/Desktop/watchdog_automation
./start_api_server.sh
```

**Keep this terminal open and your PC running!**

### Step 2: Share the Dashboard URL

Give this URL to your team members:

```
https://shraddhas-maker.github.io/NDNC/
```

### Step 3: Team Members Access

Your team members should:
1. **Connect to the same network** (same WiFi/LAN as your PC)
2. **Open the URL** in their browser
3. **Click buttons** to control the automation
4. **See real-time logs** and status updates

---

## ✅ What Works Now

| Who | What They Do | Where It Runs |
|-----|--------------|---------------|
| **You** | Run `./start_api_server.sh` | Your PC |
| **Team Members** | Open dashboard URL in browser | Their devices |
| **Team Members** | Click workflow buttons | - |
| **Automation** | Executes Selenium/Chrome | Your PC |
| **Everyone** | See real-time logs | Their browsers |

---

## 🖥️ System Architecture

```
┌─────────────────────────┐
│  Team Member's Device   │
│  (Same Network)         │
│                         │
│  Browser:               │
│  https://shraddhas-     │
│  maker.github.io/NDNC/  │
└────────────┬────────────┘
             │
             │ HTTP Requests to
             │ http://10.20.5.3:5000
             ↓
┌─────────────────────────┐
│  Your PC                │
│  IP: 10.20.5.3          │
│                         │
│  Flask API Server       │
│  Port: 5000             │
│                         │
│  Python Automation      │
│  Chrome Browser         │
│  Selenium WebDriver     │
└─────────────────────────┘
```

---

## 🔒 Security Notes

### Current Setup:
- ⚠️ **No password required** - Anyone on the network with the URL can control the automation
- ✅ **Same network only** - Only works for devices connected to your WiFi/LAN
- ✅ **Firewall protected** - Not accessible from the internet (unless port forwarding is enabled)

### Recommendations:
1. **Keep on trusted network** - Only use on secure WiFi/LAN
2. **Share URL carefully** - Only give to authorized team members
3. **Monitor usage** - Watch the terminal for activity
4. **Keep PC secure** - Lock screen when away

---

## 🐛 Troubleshooting

### Team Members See "Failed to fetch" or "Server Disconnected"

**Possible Causes:**
1. API server not running on your PC
2. Team member not on same network
3. Firewall blocking port 5000
4. IP address changed (DHCP)

**Solutions:**
1. Verify server is running: `./start_api_server.sh`
2. Check team member is on same WiFi/LAN
3. Test from your PC first: Open browser → `http://10.20.5.3:5000/api/status`
4. Check firewall: `sudo lsof -i :5000`
5. Verify IP hasn't changed: `ifconfig | grep "inet " | grep -v 127.0.0.1`

### Automation Not Starting

**Solutions:**
1. Check Chrome is installed
2. Verify Python dependencies: `pip3 list`
3. Check terminal for error messages
4. Restart API server

### IP Address Changed

If your IP address changes (common with DHCP), you need to reconfigure:

```bash
# 1. Find new IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. Update frontend/.env
cd frontend
echo 'VITE_API_URL=http://YOUR_NEW_IP:5000' > .env

# 3. Rebuild and deploy
npm run build
cd ..
git add -f frontend/dist
git commit -m "Update IP address"
git push origin main
```

---

## ⚡ Quick Commands

### Start Server
```bash
./start_api_server.sh
```

### Check Server Status
```bash
curl http://10.20.5.3:5000/api/status
```

### View Server Logs
Watch the terminal where `start_api_server.sh` is running

### Stop Server
Press `Ctrl+C` in the terminal

### Test from Another Device
```bash
curl http://10.20.5.3:5000/api/status
```

---

## 📊 Expected Behavior

### When Server is Running:
- ✅ Terminal shows: "Server is ready! Connect your React frontend."
- ✅ Dashboard shows: Green "Connected" indicator
- ✅ Can click buttons and see logs

### When Automation Runs:
- ✅ Chrome browser opens on your PC
- ✅ Terminal shows detailed logs
- ✅ Dashboard shows real-time progress
- ✅ Files are downloaded/processed
- ✅ Success/failure counts update

---

## 🎯 Next Steps

1. **Test It**: Start server and open dashboard yourself first
2. **Verify**: Check that everything works locally
3. **Share**: Give URL to team members
4. **Monitor**: Watch terminal for activity
5. **Support**: Help team members if they have issues

---

## 📞 Support

If team members have issues:
1. Verify they're on the same network
2. Check server is running
3. Test the API endpoint: `http://10.20.5.3:5000/api/status`
4. Check firewall settings
5. Review terminal logs for errors

---

## 🎉 You're All Set!

Your NDNC Automation is now configured for network access:
- ✅ Frontend deployed to GitHub Pages
- ✅ Configured with your IP: `10.20.5.3`
- ✅ Ready for team access
- ✅ Real-time monitoring enabled

**Just run `./start_api_server.sh` and share the URL!** 🚀

---

## 📝 Important Reminders

- 🖥️ **Keep your PC on** while others are using it
- 🌐 **Stay on same network** (WiFi/LAN)
- ⚡ **Keep server running** (don't close terminal)
- 🔒 **Monitor access** (watch terminal logs)
- 📱 **Share URL responsibly** (trusted team only)

