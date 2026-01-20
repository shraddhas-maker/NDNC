# 🚂 Railway Deployment Guide

## ✅ Your Project is Railway-Ready!

This project has been configured for **one-click deployment** to Railway.app.

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Railway-ready deployment"
git push origin main
```

### Step 2: Deploy to Railway

1. **Go to:** [railway.app](https://railway.app)
2. **Sign up/Login** with GitHub
3. **Click:** "New Project"
4. **Select:** "Deploy from GitHub repo"
5. **Choose:** `shraddhas-maker/NDNC`
6. **Railway will:**
   - ✅ Detect Python project
   - ✅ Install dependencies from `requirements.txt`
   - ✅ Run build command (if needed)
   - ✅ Start server using `Procfile`

### Step 3: Access Your App

After deployment completes (~2-3 minutes):

```
https://your-app-name.up.railway.app
```

✔ Frontend (React) loads at `/`  
✔ API endpoints work at `/api/*`  
✔ WebSocket connections established  
✔ Real-time logs streaming  

---

## 🔧 Railway Configuration

### Environment Variables (Optional)

If needed, add these in Railway dashboard:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | Auto-set by Railway |
| `PYTHON_VERSION` | Python version | `3.11.6` |

### Files Created for Railway

- ✅ `Procfile` - Tells Railway how to start the app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `railway.json` - Railway-specific config
- ✅ `requirements.txt` - Updated with gunicorn + eventlet

### Changes Made to Code

- ✅ `api_server.py` - Now serves React from `frontend/dist/`
- ✅ Port changed to use `PORT` env variable
- ✅ Health check endpoint added at `/health`
- ✅ Frontend API URL set to relative (same domain)

---

## 📊 What Works on Railway

### ✅ Fully Functional

- **React Frontend** - Served by Flask
- **REST API** - All `/api/*` endpoints
- **WebSocket** - Real-time updates via Socket.IO
- **File Processing** - Automation workflows
- **Statistics** - Live file counts and stats

### ⚠️ Limitations on Railway

1. **No Chrome/Selenium** - Railway doesn't support browser automation
   - **Solution:** Run automation locally, use Railway only for dashboard
   - **Alternative:** Use browserless.io or similar cloud browser service

2. **No Persistent Storage** - Files uploaded will be lost on restart
   - **Solution:** Use Railway volumes or external storage (S3)

3. **No Background Jobs** - Automation must be triggered via API
   - **Solution:** This is already implemented ✅

---

## 🎯 Recommended Setup

### For Production Use:

**Option 1: Dashboard Only (Recommended)**
- Deploy to Railway → Dashboard UI
- Run automation locally → Processing
- Connect via WebSocket → Real-time updates

**Option 2: Full Cloud**
- Deploy to Railway → Dashboard + API
- Use browserless.io → Cloud browser
- Use S3/Cloud Storage → File storage
- Update `complete_ndnc_automation.py` to use cloud browser

---

## 🔍 Troubleshooting

### Build Failed?

```bash
# Check Railway logs
railway logs

# Common issues:
- Missing dependency in requirements.txt
- Python version mismatch
- Build timeout (increase in settings)
```

### App Not Starting?

```bash
# Check deployment logs in Railway dashboard
# Verify Procfile is correct
# Test locally first:
gunicorn --worker-class eventlet -w 1 api_server:app
```

### 502 Bad Gateway?

- Health check failing at `/health`
- Port binding issue (should use `$PORT` env var)
- App crashed on startup (check logs)

---

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Discord:** https://discord.gg/railway
- **Status:** https://status.railway.app

---

## 🎉 Success!

Once deployed, share your Railway URL with your team:

```
https://your-app.up.railway.app
```

They can access the dashboard, trigger workflows, and see live logs! 🚀

