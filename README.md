# NDNC Watchdog Automation

Automatic file processing system that monitors a folder and processes new PDF and PNG files as they arrive.

## 🚀 Quick Start

### 1. Setup (First time only)

```bash
cd /Users/shraddha.s/Desktop/watchdog_automation
chmod +x setup.sh start_watchdog.sh
./setup.sh
```

### 2. Start Watchdog

**Option A: Interactive Mode** (see output in terminal)
```bash
./start_watchdog.sh
```

**Option B: Background Daemon** (auto-restart, runs 24/7)
```bash
./start_watchdog_daemon.sh start
```
See [DAEMON_SETUP.md](DAEMON_SETUP.md) for full daemon documentation.

### 3. Use the System

1. The watchdog is now monitoring: `/Users/shraddha.s/Downloads/NDNC`
2. Drop PDF or PNG files into this folder
3. The automation will automatically:
   - Detect new PDF and PNG files
   - Process them using OCR
   - Search in the NDNC dashboard
   - Match by date (within 6 months)
   - Click on matching complaints

### 4. Stop Watchdog

**Interactive Mode:**
Press `Ctrl+C` in the terminal where the watchdog is running.

**Daemon Mode:**
```bash
./stop_watchdog_daemon.sh
```

---

## 📦 Processed Files

After processing, files are automatically moved to:
```
/Users/shraddha.s/Downloads/NDNC/processed/
```

**Benefits:**
- ✅ Only new files get processed (no duplicates)
- ✅ Clean working directory
- ✅ Easy to review processed files
- ✅ Automatic archiving

**Note:** If a file with the same name already exists in the `processed` folder, a timestamp is added to prevent overwrites.

---

## 📁 Directory Structure

```
watchdog_automation/
├── watch_and_run.py          # Main watchdog script
├── ndnc_automation.py         # NDNC automation logic
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
├── start_watchdog.sh          # Start script
├── watchdog.log               # Log file (created when running)
├── venv/                      # Virtual environment (created by setup)
└── README.md                  # This file

/Users/shraddha.s/Downloads/NDNC/
├── [new files here]          # Drop new PDF/PNG files here
└── processed/                # Processed files moved here automatically
```

---

## 🔧 Configuration

Edit `watch_and_run.py` to customize:

```python
class Config:
    # Directory to monitor
    WATCH_DIRECTORY = "/Users/shraddha.s/Downloads/NDNC"
    
    # Delay before processing (seconds)
    PROCESSING_DELAY = 5
    
    # Log file location
    LOG_FILE = "/Users/shraddha.s/Desktop/watchdog_automation/watchdog.log"
```

---

## 📊 How It Works

```
┌─────────────────────┐
│  New PDF/PNG File   │
│  Dropped in Folder  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Watchdog Detects   │
│  File Creation      │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Wait 5 Seconds     │
│  (File Copy Delay)  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Process New Files  │
│  (Only Unprocessed) │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  • OCR Extraction   │
│  • Dashboard Search │
│  • Date Matching    │
│  • Click Complaint  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Move to Processed  │
│  Folder             │
└─────────────────────┘
```

---

## 📝 Features

✅ **Auto-Detection**: Monitors folder for new PDF and PNG files  
✅ **Batch Processing**: Processes multiple files at once  
✅ **OCR Support**: Reads image-based PDFs and PNG images  
✅ **Date Tolerance**: Matches dates within 6 months  
✅ **Auto-Archive**: Moves processed files to `processed/` folder automatically  
✅ **Logging**: Detailed logs for debugging  
✅ **Thread-Safe**: Handles multiple file additions safely  
✅ **Non-Blocking**: Continues watching while processing  

---

## 🔍 Monitoring

### View Logs in Real-Time

```bash
tail -f watchdog.log
```

### Check Watchdog Status

Look for these messages in the terminal:
- `📄 New PDF detected` - File was found
- `🚀 Starting automation` - Processing started
- `✅ Automation completed` - Processing finished
- `✓ Processing complete` - Ready for more files

---

## ⚡ Advanced Usage

### Run in Background

```bash
nohup ./start_watchdog.sh > /dev/null 2>&1 &
echo $! > watchdog.pid
```

### Stop Background Process

```bash
kill $(cat watchdog.pid)
rm watchdog.pid
```

### Auto-Start on Mac Boot

1. Create `~/Library/LaunchAgents/com.ndnc.watchdog.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ndnc.watchdog</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/shraddha.s/Desktop/watchdog_automation/start_watchdog.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

2. Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.ndnc.watchdog.plist
```

---

## 🐛 Troubleshooting

### Watchdog doesn't detect files
- Check the `WATCH_DIRECTORY` path in `watch_and_run.py`
- Ensure folder exists: `ls -la /Users/shraddha.s/Downloads/NDNC`

### OCR not working
- Install Tesseract: `brew install tesseract`
- Install Poppler: `brew install poppler`

### Automation fails
- Check `watchdog.log` for errors
- Verify Chrome is installed
- Ensure login credentials are correct

### Virtual environment issues
- Remove `venv` folder and run `./setup.sh` again

---

## 📧 Support

For issues or questions, check:
1. `watchdog.log` for detailed error messages
2. Terminal output for real-time status
3. Main automation script logs

---

## 🔄 Updates

To update the automation logic:
1. Stop the watchdog (`Ctrl+C`)
2. Edit `ndnc_automation.py`
3. Restart the watchdog (`./start_watchdog.sh`)

---

## ✨ Tips

- **Keep Terminal Open**: Don't close the terminal running the watchdog
- **Check Logs**: Monitor `watchdog.log` for processing status
- **Batch Upload**: Drop multiple PDFs/PNGs at once for batch processing
- **Processed Files**: Check `/Users/shraddha.s/Downloads/NDNC/processed/` for completed files
- **Reprocess Files**: Move files from `processed/` back to main folder to reprocess
- **OTP Ready**: Be ready to enter OTP when automation starts

