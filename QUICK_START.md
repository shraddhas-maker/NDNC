# 🚀 Quick Start Guide - NDNC Automation

## ✅ What Was Created

### 1. **React Frontend** (`frontend/` folder)
   - Beautiful, modern dashboard
   - Real-time console output
   - File statistics display
   - Three workflow buttons
   - Deployable to GitHub Pages (free hosting!)

### 2. **Flask API Backend** (`api_server.py`)
   - Simple REST API
   - WebSocket for real-time updates
   - Connects to your existing automation logic
   - Easy to run on any machine

### 3. **Deployment Setup**
   - GitHub Actions workflow (`.github/workflows/deploy.yml`)
   - Automatic deployment on git push
   - Comprehensive guides

## 🎯 How to Use (Right Now)

### Option 1: Test Locally (Quick Test)

```bash
# Terminal 1: Start the backend API
cd /Users/shraddha.s/Desktop/watchdog_automation
./start_api_server.sh

# Terminal 2: Start the frontend (in a new terminal)
cd /Users/shraddha.s/Desktop/watchdog_automation/frontend
npm install
npm run dev
```

Then open: **http://localhost:3000**

### Option 2: Deploy to GitHub Pages (For Team Use)

```bash
# 1. Update the repo name in frontend/vite.config.js
# Change: base: '/watchdog_automation/'
# To: base: '/YOUR_ACTUAL_REPO_NAME/'

# 2. Create GitHub repo and push
git init
git add .
git commit -m "Initial commit: NDNC Automation"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main

# 3. Enable GitHub Pages
# Go to: Settings → Pages → Source: GitHub Actions

# 4. Wait 2-3 minutes for deployment

# 5. Access your app
# https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/
```

## 📊 What Each Person Needs

### For Everyone Using the System:

1. **Frontend**: Everyone uses the same URL (GitHub Pages)
   - No installation needed
   - Just open in browser
   - Beautiful UI, works everywhere

2. **Backend**: Each person runs on their machine
   ```bash
   # One-time setup
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   pip3 install -r requirements.txt
   brew install tesseract  # macOS
   
   # Every time you use it
   ./start_api_server.sh
   ```

## 🎮 Using the Dashboard

1. **Start Backend**: Run `./start_api_server.sh`
2. **Open Dashboard**: Go to your GitHub Pages URL or `localhost:3000`
3. **Check Status**: Top-right shows connection status (green = connected)
4. **View Stats**: Four cards show file counts
5. **Run Workflow**: Click one of three buttons:
   - 🚀 **Run Both**: Review Pending + Open
   - 📋 **Review Pending Only**: Just verification
   - 📁 **Open Only**: Just uploads
6. **Monitor**: Watch live console output

## 🔧 Existing Scripts Still Work!

All your existing automation scripts still work:

```bash
# Command line (still works!)
python3 complete_ndnc_automation.py both
python3 complete_ndnc_automation.py review_pending
python3 complete_ndnc_automation.py open
python3 process_review_pending_only.py

# Shell scripts (still work!)
./run_all_workflows.sh
./run_review_pending_only.sh
./run_open.sh

# Watchdog (still works!)
./watch_open_folder.py
```

## ✨ What's Better Now?

### Before:
- ❌ Command-line only
- ❌ No visual feedback
- ❌ Hard to share
- ❌ Manual status checking
- ❌ Terminal-only logs

### After:
- ✅ Beautiful web dashboard
- ✅ Real-time visual feedback
- ✅ Easy sharing (one URL)
- ✅ Live status updates
- ✅ Clean, scrollable logs
- ✅ File statistics
- ✅ GitHub Pages hosting (FREE!)
- ✅ Professional UI

## 🎯 File Structure

```
watchdog_automation/
├── frontend/                    # NEW: React dashboard
│   ├── src/
│   │   ├── App.jsx             # Main UI logic
│   │   └── index.css           # Styling
│   ├── package.json
│   └── vite.config.js
│
├── api_server.py                # NEW: API backend
├── start_api_server.sh          # NEW: Easy startup
│
├── complete_ndnc_automation.py  # EXISTING: Main automation
├── process_review_pending_only.py  # EXISTING: Review only
├── watch_open_folder.py         # EXISTING: Watchdog
│
└── .github/workflows/deploy.yml # NEW: Auto-deployment
```

## 🧪 Quick Test

### Test Backend API:
```bash
# Start backend
./start_api_server.sh

# In another terminal, test it:
curl http://localhost:5000/api/status
# Should return JSON with file counts
```

### Test Frontend:
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
# Should see dashboard with "Connected" status
```

## 🌟 Next Steps

1. **Test locally** using Option 1 above
2. **Deploy to GitHub** using Option 2
3. **Share URL** with your team
4. **Everyone runs** `./start_api_server.sh` on their machine

## 🆘 Quick Troubleshooting

**"Disconnected" in UI**
→ Run `./start_api_server.sh` in a terminal

**"npm: command not found"**
→ Install Node.js from https://nodejs.org/

**"Port 5000 already in use"**
→ Stop other services or change port in `api_server.py`

**"Tesseract not found"**
→ Run `brew install tesseract` (macOS) or `apt-get install tesseract-ocr` (Linux)

## 📚 More Documentation

- **README.md** - Full project overview
- **DEPLOYMENT_GUIDE.md** - Detailed deployment steps
- **requirements.txt** - Python dependencies
- **frontend/package.json** - Node dependencies

---

**You're all set!** 🎉

Your automation now has a professional web interface that's easy to share and use.

**Questions?** Check DEPLOYMENT_GUIDE.md or README.md for more details.

