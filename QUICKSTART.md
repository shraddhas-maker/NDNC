# 🚀 NDNC Watchdog - Quick Start Guide

## 3 Simple Steps to Auto-Process PDFs

### Step 1: Setup (First Time Only - 2 minutes)

```bash
cd ~/Desktop/watchdog_automation
./setup.sh
```

**What it does:**
- Creates virtual environment
- Installs all dependencies
- Sets up logging
- Creates monitoring folder

---

### Step 2: Start the Watchdog (Every time you want to use it)

```bash
cd ~/Desktop/watchdog_automation
./start_watchdog.sh
```

**You'll see:**
```
============================================================
🔍 NDNC PDF Watchdog Automation
============================================================

📁 Monitoring directory: /Users/shraddha.s/Downloads/NDNC
✅ Watchdog is now active!
   Drop PDF files into the monitored folder to auto-process
   Press Ctrl+C to stop
```

---

### Step 3: Use It!

**Simply drag & drop PDF or PNG files into:**
```
/Users/shraddha.s/Downloads/NDNC
```

**The watchdog will automatically:**
1. ✅ Detect the new PDF or PNG file
2. ✅ Extract data using OCR
3. ✅ Open the NDNC dashboard
4. ✅ Search for the complaint
5. ✅ Match the date (within 6 months)
6. ✅ Click on the matching entry

**You'll see progress in the terminal:**
```
[2025-12-29 11:30:45] 📄 New PDF detected: verification_CRM-123_9080758775.pdf
[2025-12-29 11:30:50] 🚀 Starting automation for 1 new file(s)
[2025-12-29 11:31:30] ✅ Automation completed successfully!
[2025-12-29 11:31:30] ✓ Processing complete. Watching for new files...
```

**After processing:**
- ✅ Files are automatically moved to `/Users/shraddha.s/Downloads/NDNC/processed/`
- ✅ Only new files will be processed next time
- ✅ No duplicate processing!

---

## 🎯 That's It!

**Keep the terminal open** and drop PDF files as needed.  
The watchdog runs continuously until you press **Ctrl+C**.

---

## 💡 Pro Tips

### Process Multiple Files at Once
Drop several PDFs or PNGs into the folder - they'll all be processed in one batch!

### Run in Background (Advanced)
```bash
nohup ./start_watchdog.sh > /dev/null 2>&1 &
```

### View Logs
```bash
tail -f watchdog.log
```

### Check What's Being Monitored
```bash
ls -la /Users/shraddha.s/Downloads/NDNC
```

---

## 🆘 Need Help?

- **Watchdog not starting?** → Run `./setup.sh` again
- **Files not detected?** → Check they're in `/Users/shraddha.s/Downloads/NDNC`
- **OCR errors?** → Install: `brew install tesseract poppler`
- **Login issues?** → Be ready to enter OTP when prompted

---

## 🔄 Typical Workflow

1. Start watchdog once in the morning
2. Drop PDFs throughout the day
3. Each batch is processed automatically
4. Check logs for status
5. Press Ctrl+C at end of day

---

## 📧 Questions?

Check `README.md` for detailed documentation!

