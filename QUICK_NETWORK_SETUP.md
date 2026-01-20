# Quick Network Setup Reference

**Choose your deployment method:**

## 🏠 Same Network (Recommended)

```bash
# 1. Get your IP
./get_local_ip.sh

# 2. Configure frontend (replace with YOUR IP)
cd frontend
echo 'VITE_API_URL=http://192.168.1.100:5000' > .env
npm run build
cd ..

# 3. Deploy
git add frontend/.env frontend/dist
git commit -m "Network deployment"
git push origin main

# 4. Start server
./start_api_server.sh

# 5. Share URL
# https://YOUR_GITHUB_USERNAME.github.io/NDNC/
```

---

## 🌍 Remote Access (ngrok)

```bash
# 1. Install ngrok (first time only)
brew install ngrok  # macOS
# OR download from https://ngrok.com/download

# 2. Authenticate (first time only)
ngrok config add-authtoken YOUR_AUTH_TOKEN

# 3. Start API server
./start_api_server.sh

# 4. Start ngrok (new terminal)
./setup_ngrok.sh
# OR: ngrok http 5000

# 5. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 6. Update frontend
cd frontend
echo 'VITE_API_URL=https://abc123.ngrok.io' > .env
npm run build
cd ..

# 7. Deploy
git add frontend/.env frontend/dist
git commit -m "ngrok deployment"
git push origin main

# 8. Share URL
# https://YOUR_GITHUB_USERNAME.github.io/NDNC/
```

---

## 🔄 Switch Back to Local

```bash
cd frontend
rm .env
npm run build
cd ..
git add frontend
git commit -m "Back to local mode"
git push origin main
```

---

## ✅ Test Connection

```bash
# Test API server
curl http://localhost:5000/api/status

# Test from network (replace IP)
curl http://192.168.1.100:5000/api/status
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Failed to fetch" | 1. Check server is running<br>2. Verify IP in .env<br>3. Check firewall |
| Changes not showing | 1. Clear browser cache<br>2. Rebuild: `npm run build`<br>3. Hard refresh |
| ngrok URL changed | Update .env with new URL and redeploy |

---

## 📚 Full Documentation

See [NETWORK_DEPLOYMENT.md](./NETWORK_DEPLOYMENT.md) for complete guide.

