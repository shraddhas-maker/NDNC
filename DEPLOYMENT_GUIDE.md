# 🚀 NDNC Automation - Deployment Guide

## 📋 Overview

This guide shows you how to deploy the NDNC Automation system with:
- **Frontend**: React app hosted on GitHub Pages (free, accessible to everyone)
- **Backend**: Flask API running locally on each user's machine

## 🎯 Architecture

```
┌─────────────────────────────────────────┐
│  GitHub Pages (Everyone Accesses)      │
│  https://yourusername.github.io        │
│  React Frontend (UI)                    │
└─────────────────────────────────────────┘
                    ↓
         Connects via WebSocket
                    ↓
┌─────────────────────────────────────────┐
│  User's Local Machine                   │
│  localhost:5000                         │
│  Flask API + Python Automation          │
│  - File processing                      │
│  - Browser automation                   │
│  - OCR validation                       │
└─────────────────────────────────────────┘
```

## 📦 Part 1: Deploy Frontend to GitHub Pages

### Step 1: Create GitHub Repository

```bash
cd /Users/shraddha.s/Desktop/watchdog_automation

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: NDNC Automation with React frontend"

# Create GitHub repo (via GitHub website or CLI)
# Then add remote
git remote add origin https://github.com/YOUR_USERNAME/watchdog_automation.git

# Push to GitHub
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow will automatically deploy on every push to `main`

### Step 3: Update Frontend Configuration

Before pushing, update the repository name in `frontend/vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/YOUR_REPO_NAME/',  // Change this to your actual repo name
  // ...
})
```

### Step 4: Build and Deploy

The GitHub Action will automatically:
1. Install dependencies
2. Build the React app
3. Deploy to GitHub Pages

Your frontend will be available at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/
```

## 🖥️ Part 2: Setup Backend (For Each User)

### Prerequisites

Each user needs:
- Python 3.8+
- Chrome browser
- Tesseract OCR

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/watchdog_automation.git
cd watchdog_automation

# 2. Install Python dependencies
pip3 install -r requirements.txt

# 3. Install Tesseract OCR
# macOS:
brew install tesseract

# Linux (Ubuntu/Debian):
sudo apt-get install tesseract-ocr

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 4. Configure email (optional)
# Edit api_server.py and change:
# EMAIL = "your-email@exotel.com"
```

### Running the Backend

```bash
# Start the API server
./start_api_server.sh

# Or manually:
python3 api_server.py
```

The API server will start on `http://localhost:5000`

## 🌐 Part 3: Using the System

### For End Users

1. **Open the web app**: Go to `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`
2. **Start backend**: Run `./start_api_server.sh` on your local machine
3. **Connect**: The frontend will automatically connect to `localhost:5000`
4. **Use the dashboard**: Select and run workflows from the web interface

### Workflow Options

| Workflow | Description |
|----------|-------------|
| **Run Both** | Processes Review Pending + Open complaints |
| **Review Pending Only** | Only processes Review Pending files |
| **Open Only** | Only processes Open complaints |

## 🔧 Configuration

### Backend Configuration (`api_server.py`)

```python
# Update your email
EMAIL = "your-email@exotel.com"

# Folder structure (automatically created)
BASE_DIR = Path.home() / "Downloads" / "NDNC"
REVIEW_PENDING_DIR = BASE_DIR / "review_pending"
OPEN_DIR = BASE_DIR / "open"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_REVIEW_DIR = BASE_DIR / "processed_review"
```

### Frontend Configuration (`frontend/src/App.jsx`)

By default, the frontend connects to `localhost:5000`. No changes needed for local development.

## 📱 Development Mode

### Run Frontend Locally

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Frontend will be available at http://localhost:3000
```

### Run Backend Locally

```bash
# In project root
./start_api_server.sh

# Backend will be available at http://localhost:5000
```

## 🚢 Production Deployment Checklist

- [ ] Update `EMAIL` in `api_server.py`
- [ ] Update `base` in `frontend/vite.config.js` with your repo name
- [ ] Create GitHub repository
- [ ] Enable GitHub Pages (GitHub Actions)
- [ ] Push code to GitHub
- [ ] Wait for GitHub Action to complete
- [ ] Access frontend at `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`
- [ ] Each user runs `./start_api_server.sh` on their machine

## 🔍 Troubleshooting

### Frontend can't connect to backend

**Issue**: "Disconnected" status in the UI

**Solution**:
1. Ensure API server is running (`./start_api_server.sh`)
2. Check if port 5000 is available
3. Open browser console (F12) and check for WebSocket errors

### GitHub Pages not deploying

**Issue**: Website shows 404

**Solution**:
1. Check GitHub Actions tab for deployment status
2. Ensure `base` path in `vite.config.js` matches your repo name
3. Verify GitHub Pages is enabled in repository settings

### Tesseract not found

**Issue**: OCR fails with "tesseract not found"

**Solution**:
```bash
# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr

# Verify installation
tesseract --version
```

### Permission errors on macOS

**Issue**: "Operation not permitted"

**Solution**:
```bash
# Give terminal full disk access
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add Terminal.app or your terminal emulator
```

## 📊 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS 10.15+, Linux, Windows 10+ |
| **Python** | 3.8 or higher |
| **RAM** | 4 GB minimum |
| **Disk Space** | 2 GB free space |
| **Browser** | Chrome 90+ |
| **Internet** | Stable connection required |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **RAM** | 8 GB or more |
| **CPU** | 4 cores or more |
| **Disk Space** | 5 GB free space |

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the console output
3. Check browser console (F12 → Console)
4. Verify all system dependencies are installed

## 📝 Notes

- **Frontend is public**: Anyone with the URL can access the UI
- **Backend is private**: Each user runs their own backend locally
- **No data sharing**: Each user's files and automation are independent
- **Free hosting**: GitHub Pages is completely free
- **Auto-updates**: Push to `main` branch to update the frontend for everyone

## 🎉 Benefits of This Setup

✅ **Easy Sharing**: Share one URL with your entire team  
✅ **Free Hosting**: No server costs for the frontend  
✅ **Privacy**: Each user's automation runs on their own machine  
✅ **Auto-Deploy**: Push code → automatic deployment  
✅ **Cross-Platform**: Works on macOS, Linux, and Windows  
✅ **No Complex Setup**: Users just run one script  
✅ **Beautiful UI**: Modern, responsive React interface  
✅ **Real-time Updates**: Live console output via WebSocket  

---

**Ready to deploy!** Follow the steps above and you'll have a production-ready system in minutes. 🚀

