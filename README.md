# 🚂 NDNC Automation - Railway Deployment

## ✅ Your App is 100% Railway-Ready!

---

## 🚀 Quick Deploy to Railway (3 Steps)

### Step 1: Open Railway

Go to: **[railway.app](https://railway.app)**

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: **`shraddhas-maker/NDNC`**
4. Click **"Deploy Now"**

### Step 3: Wait for Deployment

Railway will automatically:
- ✅ Detect Python project
- ✅ Install all dependencies
- ✅ Build React frontend (already built)
- ✅ Start server with gunicorn
- ✅ Assign public URL

**Deployment time:** ~2-3 minutes

---

## 🎯 After Deployment

### Your Live URL

```
https://your-app-name.up.railway.app
```

**What works:**
- ✅ React Dashboard at `/`
- ✅ API endpoints at `/api/*`
- ✅ WebSocket for real-time updates
- ✅ File statistics and controls
- ✅ Pause/Resume/Stop workflows

---

## 📁 Project Structure

```
watchdog_automation/
├── api_server.py              # Flask backend (serves React + API)
├── complete_ndnc_automation.py # Automation logic
├── process_review_pending_only.py
├── requirements.txt           # Python dependencies
├── Procfile                   # Railway start command
├── runtime.txt                # Python 3.11
├── railway.json               # Railway config
└── frontend/
    ├── dist/                  # Built React app (served by Flask)
    └── src/                   # React source code
```

---

## ⚙️ How It Works

### 1. Flask Serves Everything

```python
# api_server.py serves:
GET /              → React frontend (from frontend/dist/)
GET /api/status    → Backend API
GET /health        → Health check for Railway
WS  /socket.io     → WebSocket for real-time updates
```

### 2. Gunicorn with Eventlet

```
Procfile: gunicorn --worker-class eventlet -w 1 api_server:app
```

- Uses **eventlet** for WebSocket support
- Binds to Railway's `$PORT` variable
- Single worker for Socket.IO compatibility

### 3. React Frontend

- Pre-built and committed to `frontend/dist/`
- API calls use **relative URLs** (same domain as backend)
- No CORS issues (served from same origin)

---

## 🔧 Configuration (Optional)

### Environment Variables in Railway

Add these in Railway dashboard if needed:

| Variable | Value | Purpose |
|----------|-------|---------|
| `PORT` | Auto-set by Railway | Server port |
| `PYTHON_VERSION` | `3.11.6` | From runtime.txt |

No configuration needed - works out of the box! ✅

---

## ⚠️ Important: Selenium/Chrome Limitations

### What DOESN'T Work on Railway

Railway doesn't support:
- ❌ Chrome browser
- ❌ Selenium WebDriver
- ❌ Browser automation

### Recommended Setup

**Option A: Dashboard Only (Best)**
```
Railway:  React Dashboard + API + WebSocket
Your PC:  Chrome automation
```

**Option B: Cloud Browser**
```
Railway:     Flask + React
Browserless: Cloud Chrome (paid service)
Update:      complete_ndnc_automation.py to use remote browser
```

**For now, use Option A:**
1. Deploy dashboard to Railway
2. Run automation locally with `./start_api_server.sh`
3. Connect both UIs to see live updates

---

## 🐛 Troubleshooting

### Build Failed?

```bash
# Check Railway logs
railway logs

# Test locally first:
gunicorn --worker-class eventlet -w 1 api_server:app
```

### 502 Bad Gateway?

- Check `/health` endpoint works
- Verify `PORT` env variable is used
- Check logs for startup errors

### WebSocket Not Connecting?

- Ensure using `eventlet` worker class
- Check CORS settings in `api_server.py`
- Verify Railway URL in browser console

---

## 📊 Testing Locally (Before Deploy)

```bash
# Install gunicorn and eventlet
pip install gunicorn eventlet

# Test production server
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8080 api_server:app

# Open browser
http://localhost:8080
```

Should see:
- ✅ React dashboard loads
- ✅ "Connected" indicator (green)
- ✅ File counts displayed
- ✅ Console logs streaming

---

## 🎉 Deployment Checklist

- [x] ✅ `Procfile` created
- [x] ✅ `runtime.txt` added
- [x] ✅ `railway.json` configured
- [x] ✅ `requirements.txt` updated (gunicorn + eventlet)
- [x] ✅ `api_server.py` serves React from `frontend/dist/`
- [x] ✅ Frontend rebuilt with relative API URL
- [x] ✅ Port uses `$PORT` env variable
- [x] ✅ Health check endpoint at `/health`
- [x] ✅ Pushed to GitHub
- [x] ✅ Ready to deploy! 🚀

---

## 🚀 Deploy Now!

**Go to:** [railway.app/new](https://railway.app/new)

1. Connect GitHub
2. Select `shraddhas-maker/NDNC`
3. Click **Deploy**
4. Share your Railway URL!

---

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **GitHub Issues:** https://github.com/shraddhas-maker/NDNC/issues

---

**Built with ❤️ for Exotel NDNC Compliance**

