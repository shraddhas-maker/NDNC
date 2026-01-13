# 🌐 NDNC Automation Web UI Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Start the Web UI

```bash
./start_web_ui.sh
```

Or manually:

```bash
python3 web_ui.py
```

### 3. Open Browser

Navigate to: **http://localhost:5000**

---

## 📊 Dashboard Features

### **Real-Time Statistics**

- **Review Pending**: Files waiting for verification
- **Open Complaints**: Files ready for upload
- **Processed**: Successfully completed files
- **Failed**: Files that encountered errors

### **Workflow Controls**

1. **Run Both Workflows** (Default)
   - Processes Review Pending files first
   - Then processes Open complaints
   - Automatically selected as default

2. **Review Pending Only**
   - Only processes files in `~/Downloads/NDNC/review_pending/`
   - Downloads from dashboard if needed

3. **Open Complaints Only**
   - Only processes files in `~/Downloads/NDNC/open/`

### **Live Console**

- Real-time log output
- Color-coded messages (success, error, warning)
- Auto-scrolling
- Clear button to reset console

---

## 🎯 How It Works

### **Smart Skip Logic**

The system automatically skips workflows if no files are present:

```
✅ If Review Pending folder is empty → Skips and shows message
✅ If Open folder is empty → Skips and shows message
✅ If both folders are empty → Skips entire workflow
```

**Example Messages:**
```
⚠️  No files in review_pending folder. Skipping workflow.
⚠️  No files in open folder. Skipping workflow.
⚠️  No files in review_pending or open folders. Skipping all workflows.
```

### **Workflow Execution**

```
┌─────────────────────────────────────┐
│  Click "Run Both Workflows"         │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  System checks file counts          │
│  - review_pending: X files          │
│  - open: Y files                    │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  If files exist:                    │
│  1. Login to NDNC Dashboard         │
│  2. Process Review Pending          │
│  3. Process Open                    │
│  4. Show completion message         │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  If no files:                       │
│  Show skip message instantly        │
└─────────────────────────────────────┘
```

---

## 💡 UI Components

### **Status Badge (Top Right)**

- **Green Dot + "Connected"**: WebSocket connected, real-time updates active
- **Red Dot + "Disconnected"**: Connection lost, try refreshing

### **Workflow Status**

- **Gray Dot + "Ready"**: No workflow running
- **Green Dot (Pulsing) + "Running: X"**: Workflow in progress

### **Control Buttons**

- **Disabled (grayed out)**: Workflow is running
- **Enabled (colored)**: Ready to start

---

## 🎨 Visual Indicators

### **Colors**

- 🟢 **Green**: Success, Connected, Processed
- 🔴 **Red**: Failed, Disconnected, Errors
- 🟡 **Yellow**: Review Pending, Warnings
- 🔵 **Blue**: Open Complaints, Info
- 🟣 **Purple**: Primary actions

### **Animations**

- **Pulsing Dot**: Active connection or running workflow
- **Hover Effects**: All interactive elements have smooth hover animations
- **Auto-scroll**: Console automatically scrolls to show latest logs

---

## 🔧 Advanced Features

### **Performance Optimizations**

The web UI version has reduced sleep times for faster execution:

- Page loads: **3s** → **2-3s**
- Browser startup: **2s** → **1s**
- Navigation: **5s** → **3s**

### **Real-Time Updates via WebSocket**

- Log messages stream live to console
- Status updates happen instantly
- File counts refresh automatically every 10 seconds

### **Smart Error Handling**

- Connection loss detection
- Automatic reconnection attempts
- Clear error messages in console

---

## 📱 Responsive Design

The UI is fully responsive and works on:

- 🖥️ Desktop (1920x1080+)
- 💻 Laptop (1366x768+)
- 📱 Tablet (768x1024)
- 📱 Mobile (375x667+)

---

## 🛠️ Troubleshooting

### **"Connection Failed" / "Disconnected"**

1. Check if server is running
2. Refresh the page (F5)
3. Check console for errors (F12)

### **"Workflow Already Running"**

- Wait for current workflow to complete
- Status will change to "Ready" when done

### **Files Not Detected**

1. Check folder structure:
   ```
   ~/Downloads/NDNC/
   ├── review_pending/
   └── open/
   ```

2. Refresh page to update file counts

### **Browser Compatibility**

Works best on:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ Internet Explorer (not recommended)

---

## 🔐 Security

- Server runs on **localhost** only by default
- No authentication required (local use)
- WebSocket secured by Flask secret key

---

## 🚦 Port Configuration

**Default**: `http://localhost:5000`

To change port, edit `web_ui.py`:

```python
socketio.run(app, host='0.0.0.0', port=5000, debug=False)
#                                      ^^^^
#                                    Change this
```

---

## 📸 Screenshots

### Main Dashboard
- Beautiful dark theme
- Real-time statistics
- Large, clear buttons

### Live Console
- Monospace font for readability
- Color-coded output
- Timestamp on each line
- Auto-scrolling

---

## 🎯 Default Behavior

When you click **"Run Both Workflows"**:

1. ✅ Automatically selects "both" (option 3)
2. ✅ Checks for files in both folders
3. ✅ Skips empty folders with clear messages
4. ✅ Shows real-time progress
5. ✅ Updates statistics dynamically

**No more command-line selections needed!**

---

## 🆘 Support

For issues or questions:

1. Check console output (in web UI)
2. Check terminal where `web_ui.py` is running
3. Review `WEB_UI_GUIDE.md` (this file)

---

## ✨ Features Summary

| Feature | Status |
|---------|--------|
| Real-time logs | ✅ |
| File count display | ✅ |
| Auto skip empty folders | ✅ |
| Default to "both" workflows | ✅ |
| Beautiful UI | ✅ |
| Responsive design | ✅ |
| WebSocket updates | ✅ |
| Error handling | ✅ |
| Performance optimized | ✅ |

---

**Enjoy the new Web UI! 🎉**

