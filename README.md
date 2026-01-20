# 🚀 NDNC Automation System

**Automated complaint processing for NDNC (National Do Not Call) registry with a modern React dashboard.**

![Status](https://img.shields.io/badge/status-active-success.svg)
![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎨 **Modern React UI** - Beautiful, responsive dashboard accessible from any browser
- 🤖 **Full Automation** - Automated browser control, OCR validation, and file processing
- 🌐 **Network Deployment** - Run on your PC, control from any device on your network
- 📊 **Real-time Monitoring** - Live console output and file statistics
- 🔄 **Multiple Workflows** - Review Pending, Open complaints, or both together
- 🌍 **GitHub Pages Hosting** - Free, easy deployment for the frontend
- 🎯 **OCR Validation** - Comprehensive document authenticity checks (URL, logo, phone, date)
- ⏸️ **Pause/Resume/Stop** - Full control over automation workflows

## 🎯 Quick Start

### For Users (Running the System)

1. **Clone the repository:**
```bash
   git clone https://github.com/YOUR_USERNAME/watchdog_automation.git
   cd watchdog_automation
```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Start the backend:**
```bash
   ./start_api_server.sh
```

4. **Open the web UI:**
   - Go to: `https://YOUR_USERNAME.github.io/watchdog_automation/`
   - Or run locally: `cd frontend && npm install && npm run dev`

5. **Start automating!** 🎉

### For Network Deployment (Let Others Use It)

**Want to run the server on your PC and let others control it from their browsers?**

See **[NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)** for complete network setup guide.

**Quick Setup:**
```bash
./get_local_ip.sh           # Get your IP address
cd frontend
echo 'VITE_API_URL=http://YOUR_IP:5000' > .env
npm run build
cd .. && git add frontend && git commit -m "Network deployment" && git push
./start_api_server.sh       # Keep running!
```

Others can now access: `https://YOUR_GITHUB_USERNAME.github.io/watchdog_automation/`

### For Administrators (Initial Deployment)

See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for complete deployment instructions.

## 📁 Project Structure

```
watchdog_automation/
├── frontend/                    # React frontend (deployed to GitHub Pages)
│   ├── src/
│   │   ├── App.jsx             # Main React app
│   │   ├── index.css           # Styling
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   └── vite.config.js
├── complete_ndnc_automation.py  # Main automation logic
├── api_server.py                # Flask API backend
├── process_review_pending_only.py
├── watch_open_folder.py         # Watchdog for open folder
├── start_api_server.sh          # Backend startup script
├── requirements.txt             # Python dependencies
└── DEPLOYMENT_GUIDE.md          # Deployment instructions
```

## 🔧 How It Works

### Architecture

```
┌──────────────────────────────────┐
│   React Frontend (GitHub Pages)  │
│   Everyone accesses the same UI  │
└──────────────────────────────────┘
            ↓ WebSocket
┌──────────────────────────────────┐
│   Flask API (Local Machine)      │
│   - WebSocket server              │
│   - REST endpoints                │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│   Python Automation               │
│   - Selenium browser automation   │
│   - OCR with Tesseract           │
│   - File processing               │
│   - Document validation           │
└──────────────────────────────────┘
```

### Workflows

#### 1️⃣ Review Pending Workflow
- Downloads files from NDNC dashboard
- Validates documents (OCR checks for URL, logo, phone, date)
- Searches for complaints by phone number
- Verifies and processes each file
- Moves to `processed_review/` folder

#### 2️⃣ Open Complaints Workflow
- Processes files from `open/` folder
- Uploads documents to NDNC portal
- Validates and submits complaints
- Moves to `processed/` folder

#### 3️⃣ Both Workflows
- Runs Review Pending first
- Then processes Open complaints
- Complete end-to-end automation

## 📊 Dashboard Features

### Statistics Cards
- **Review Pending**: Files waiting for verification
- **Open Complaints**: Files ready to upload
- **Processed**: Successfully completed files
- **Failed**: Files that encountered errors

### Control Panel
- **Run Both Workflows**: Complete automation
- **Review Pending Only**: Just verification
- **Open Only**: Just uploads
- Real-time workflow status indicator

### Live Console
- Real-time log output
- Timestamped messages
- Auto-scrolling
- Clear button

## 🛠️ Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 18+ (for frontend development)
- **Chrome**: Latest version
- **Tesseract OCR**: Latest version

### Python Packages
```
selenium, PyPDF2, pytesseract, opencv-python, Pillow
Flask, Flask-SocketIO, Flask-CORS
openpyxl, watchdog, numpy
```

### Installation
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Tesseract OCR
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Linux
```

## 📝 Configuration

### Email Setup
Edit `api_server.py`:
```python
EMAIL = "your-email@exotel.com"
```

### Folder Structure
Files are automatically organized:
```
~/Downloads/NDNC/
├── review_pending/      # Files to verify
├── open/                # Files to upload
├── processed/           # Completed open files
└── processed_review/    # Completed review files
```

## 🚀 Usage

### Web UI (Recommended)
1. Start backend: `./start_api_server.sh`
2. Open browser: `https://YOUR_USERNAME.github.io/watchdog_automation/`
3. Click workflow buttons
4. Monitor progress in live console

### Command Line
```bash
# Run both workflows
python3 complete_ndnc_automation.py both

# Review pending only
python3 complete_ndnc_automation.py review_pending

# Open only
python3 complete_ndnc_automation.py open
```

## 🔍 OCR Validation

The system performs comprehensive document validation:

### ✅ Checks Performed
1. **URL Detection**: Verifies URL presence in document
2. **Logo Detection**: Checks for company/brand logos
3. **Phone Number**: Validates phone number matches
4. **Date Range**: Ensures date is within 6 months
5. **Document Authenticity**: Multiple validation layers

### 🧠 OCR Engine
- **6-layer OCR system** with image preprocessing
- **OpenCV processing**: Grayscale, thresholding, CLAHE, sharpening
- **Multiple PSM modes**: 6, 3, 11, 12 for best accuracy
- **Address bar extraction**: Specialized URL detection
- **Fallback mechanisms**: Filename date matching

## 📱 Browser Automation

### Features
- **Persistent sessions**: No repeated OTP entry
- **Smart waiting**: Adaptive element detection
- **Modal handling**: Automatic dialog management
- **Error recovery**: Robust exception handling
- **JavaScript execution**: Bypass interception issues

## 🆘 Troubleshooting

### "Disconnected" Status
→ Ensure `./start_api_server.sh` is running

### "Login Failed"
→ Check email configuration and OTP timeout (5 minutes)

### OCR Not Working
→ Verify Tesseract is installed: `tesseract --version`

### Files Not Processing
→ Check file formats (PDF, PNG, JPG, JPEG supported)

### Port 5000 Already in Use
→ Stop other services using port 5000 or change port in `api_server.py`

## 🎯 Deployment

### Quick Deploy to GitHub Pages

```bash
# 1. Push to GitHub
git push origin main

# 2. Enable GitHub Pages
# Settings → Pages → Source: GitHub Actions

# 3. Access your app
# https://YOUR_USERNAME.github.io/watchdog_automation/
```

See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for detailed instructions.

## 🤝 Team Usage

### Share with Team
1. Deploy frontend to GitHub Pages (one-time setup)
2. Share the URL with your team
3. Each person runs `./start_api_server.sh` on their machine
4. Everyone uses the same beautiful UI

### Benefits
- ✅ Single UI for entire team
- ✅ No server costs
- ✅ Each user's data stays private
- ✅ Easy updates (just push to GitHub)

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Credits

Built with:
- [React](https://react.dev/) - UI framework
- [Vite](https://vitejs.dev/) - Build tool
- [Flask](https://flask.palletsprojects.com/) - API backend
- [Socket.IO](https://socket.io/) - Real-time communication
- [Selenium](https://www.selenium.dev/) - Browser automation
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Text extraction

## 📞 Support

For issues, questions, or contributions:
- Check troubleshooting section above
- Review `DEPLOYMENT_GUIDE.md`
- Open an issue on GitHub

---

**Made with ❤️ for efficient NDNC complaint management**

🌟 **Star this repo if you find it helpful!**
