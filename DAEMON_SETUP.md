# 🚀 NDNC Watchdog - Background Daemon Setup

## Overview
This guide shows you how to run the NDNC Watchdog as a background service that automatically restarts if it crashes.

---

## 🎯 Quick Start - Run as Background Service

### Step 1: Make Scripts Executable
```bash
cd /Users/shraddha.s/Desktop/watchdog_automation
chmod +x start_watchdog_daemon.sh stop_watchdog_daemon.sh
```

### Step 2: Start the Daemon
```bash
./start_watchdog_daemon.sh start
```

**What happens:**
- ✅ Watchdog starts in the background
- ✅ Automatically restarts if it crashes
- ✅ Runs continuously until you stop it
- ✅ All output logged to `watchdog_daemon.log`

### Step 3: Check Status
```bash
./start_watchdog_daemon.sh status
```

### Step 4: Stop the Daemon
```bash
./stop_watchdog_daemon.sh
```

---

## 📋 Daemon Commands

### Start Daemon
```bash
./start_watchdog_daemon.sh start
```
Starts the watchdog daemon in the background.

### Stop Daemon
```bash
./stop_watchdog_daemon.sh
```
Stops the watchdog daemon completely.

### Restart Daemon
```bash
./start_watchdog_daemon.sh restart
```
Stops and restarts the daemon.

### Check Status
```bash
./start_watchdog_daemon.sh status
```
Shows if the daemon is running.

---

## 📁 Log Files

### Daemon Log
```
/Users/shraddha.s/Desktop/watchdog_automation/watchdog_daemon.log
```
Contains daemon status, restarts, and all automation output.

### Watchdog Log
```
/Users/shraddha.s/Desktop/watchdog_automation/watchdog.log
```
Contains file detection and processing logs.

### View Logs in Real-Time
```bash
# View daemon log
tail -f watchdog_daemon.log

# View watchdog log
tail -f watchdog.log
```

---

## 🔄 Auto-Restart Feature

The daemon automatically monitors the watchdog process:

- **Every 10 seconds**: Checks if watchdog is running
- **If crashed**: Automatically restarts it
- **Logs everything**: All restarts are logged with timestamps

**Benefits:**
- ✅ No manual intervention needed
- ✅ Continues working even after errors
- ✅ Survives browser crashes
- ✅ Self-healing system

---

## 💻 Auto-Start on Mac Boot (Optional)

If you want the watchdog to start automatically when your Mac boots:

### Step 1: Create LaunchAgent
```bash
cat > ~/Library/LaunchAgents/com.ndnc.watchdog.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ndnc.watchdog</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/shraddha.s/Desktop/watchdog_automation/start_watchdog_daemon.sh</string>
        <string>start</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/shraddha.s/Desktop/watchdog_automation/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/shraddha.s/Desktop/watchdog_automation/launchd.error.log</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/shraddha.s/Desktop/watchdog_automation</string>
</dict>
</plist>
EOF
```

### Step 2: Load LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.ndnc.watchdog.plist
```

### Step 3: Check Status
```bash
launchctl list | grep ndnc
```

### To Disable Auto-Start
```bash
launchctl unload ~/Library/LaunchAgents/com.ndnc.watchdog.plist
```

---

## 🔍 Monitoring

### Check if Daemon is Running
```bash
ps aux | grep watchdog
```

### Check PID File
```bash
cat /Users/shraddha.s/Desktop/watchdog_automation/watchdog_daemon.pid
```

### Check Logs
```bash
# Last 50 lines of daemon log
tail -50 watchdog_daemon.log

# Follow daemon log
tail -f watchdog_daemon.log

# Search for errors
grep "ERROR" watchdog_daemon.log
```

---

## 🛠️ Troubleshooting

### Daemon Won't Start
**Check:**
1. Is setup complete? Run `./setup.sh`
2. Are scripts executable? Run `chmod +x *.sh`
3. Check log file for errors: `tail watchdog_daemon.log`

### Watchdog Keeps Crashing
**Check:**
1. Review `watchdog_daemon.log` for error messages
2. Ensure browser (Chrome) is installed
3. Check if OTP is being entered (first run only)
4. Verify file permissions in `/Users/shraddha.s/Downloads/NDNC`

### Can't Stop Daemon
```bash
# Force stop everything
./stop_watchdog_daemon.sh

# If still running, find and kill manually
ps aux | grep watchdog
kill -9 <PID>
```

### Daemon Log Too Large
```bash
# Archive old log
mv watchdog_daemon.log watchdog_daemon.log.old

# Or clear it
> watchdog_daemon.log
```

---

## 📊 Daemon vs Normal Mode

### Normal Mode (./start_watchdog.sh)
- ✓ Interactive terminal
- ✓ See output in real-time
- ✓ Browser stays open after processing
- ✓ Manual OTP entry visible
- ✗ Stops if terminal closes
- ✗ No auto-restart on crash

### Daemon Mode (./start_watchdog_daemon.sh)
- ✓ Runs in background
- ✓ Auto-restarts on crash
- ✓ Browser closes after processing (headless)
- ✓ Survives terminal close
- ✓ Can run on boot
- ✗ Output only in log files
- ⚠️  Still need to enter OTP on first run

---

## 🎛️ Configuration

Edit `watch_and_run.py` to customize:

```python
class Config:
    WATCH_DIRECTORY = "/Users/shraddha.s/Downloads/NDNC"
    PROCESSING_DELAY = 5  # seconds
    LOG_FILE = "/Users/shraddha.s/Desktop/watchdog_automation/watchdog.log"
```

---

## ✅ Best Practices

1. **Start daemon once**: Use `./start_watchdog_daemon.sh start`
2. **Check logs regularly**: `tail -f watchdog_daemon.log`
3. **Monitor disk space**: Log files can grow large
4. **Restart after code changes**: `./start_watchdog_daemon.sh restart`
5. **Use status command**: Check if running before starting

---

## 🆘 Getting Help

### View All Processes
```bash
ps aux | grep -E "watchdog|ndnc"
```

### Kill All Watchdog Processes
```bash
pkill -f "watchdog"
./stop_watchdog_daemon.sh
```

### Fresh Start
```bash
./stop_watchdog_daemon.sh
rm -f watchdog_daemon.pid
./start_watchdog_daemon.sh start
```

---

## 📝 Summary

**For development/testing:**
```bash
./start_watchdog.sh  # Interactive mode
```

**For production/24/7 operation:**
```bash
./start_watchdog_daemon.sh start  # Background daemon
```

**To stop:**
```bash
./stop_watchdog_daemon.sh  # Stop everything
```

That's it! Your watchdog will now run in the background and automatically restart if anything goes wrong! 🎉

