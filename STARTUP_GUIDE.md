# 🚀 Nemesis Backend & Frontend Startup Guide

## Quick Start (3 Easy Steps)

### **Setup (First Time Only)**
```bash
cd /home/kali/Desktop/Nemesis
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
cd frontend && npm install && cd ..
```

---

## **Running Nemesis**

### **Terminal 1: Start the Backend API Server** ⚡
```bash
cd /home/kali/Desktop/Nemesis
chmod +x start_backend.sh
sudo ./start_backend.sh
```
**Expected Output:**
```
✓ Running with root privileges (full network capture enabled)
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
**Keep this terminal open** - the API server must stay running!

---

### **Terminal 2: Test the API** 🧪
After the backend starts, run tests in a new terminal:
```bash
cd /home/kali/Desktop/Nemesis
chmod +x test.sh
./test.sh
```
**Expected Output:**
```
✓ API is running
Testing GET /status
✓ Status endpoint (200): [database info and stats]
Testing GET /alerts...
✓ Alerts endpoint (200): []
[... more test results ...]
✅ Test suite complete!
```

---

### **Terminal 3: Start the Frontend Dashboard** 🎨
In a third terminal:
```bash
cd /home/kali/Desktop/Nemesis
chmod +x start_frontend.sh
./start_frontend.sh
```
**Expected Output:**
```
✓ Dependencies already installed
🎨 Starting frontend dev server...
VITE v5.x.x  ready in 123 ms
➜  local:   http://localhost:5173/
```

---

## **Access the Application**

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend Dashboard** | http://localhost:5173 | Real-time SOC monitoring |
| **API Status** | http://localhost:8000/status | Backend health check |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **WebSocket** | ws://localhost:8000/ws | Real-time data streaming |

---

## **What Each Component Does**

### ✅ Backend API (`start_backend.sh`)
- Runs FastAPI server on port 8000
- Initializes SQLite database (`nemesis.db`)
- Collects network data with Agents Alpha, Beta, Gamma
- Provides REST endpoints for data access
- Streams real-time data via WebSocket

### ✅ Frontend Dashboard (`start_frontend.sh`)
- React dashboard on port 5173
- Displays system status, alerts, traffic, anomalies
- Connects to WebSocket for live updates
- Shows devices and their risk levels

### ✅ Tests (`test.sh`)
- Verifies API is responding
- Tests all 5 main endpoints
- Checks database connectivity
- Validates data persistence

---

## **Database & Data Persistence**

The system stores all SOC data automatically:

```
Database: nemesis.db (SQLite)
Location: /home/kali/Desktop/Nemesis/nemesis.db

Tables:
  • devices           - Network devices ({MAC, IP, risk_level})
  • alerts            - Security alerts ({timestamp, message, level})
  • traffic_logs      - Network traffic ({src_ip, dst_ip, packets})
  • honeypot_interactions - Honeypot attack logs
  • system_metrics    - Performance metrics (CPU, memory, network)
  • vulnerabilities   - Known CVEs and exposures
  • configurations    - System settings and policies
```

**Endpoints to Query Data:**
- `GET /status` - Database statistics
- `GET /alerts` - Retrieved alerts
- `GET /traffic?limit=50` - Network traffic logs
- `GET /honeypots/detection?limit=50` - Honeypot events
- `GET /anomalies?limit=50` - Detected anomalies

---

## **Common Issues & Solutions**

### ❌ **"Connection refused" when running tests**
**Problem:** Backend API server isn't running
**Solution:** 
```bash
# In Terminal 1, make sure this is running:
sudo ./start_backend.sh
# Keep this terminal open and running
```

### ❌ **"Permission denied" for network capture**
**Problem:** Network packet capture requires root privileges
**Solution:**
```bash
# Always run backend with sudo:
sudo ./start_backend.sh
```

### ❌ **"Module not found" errors**
**Problem:** Dependencies not installed
**Solution:**
```bash
source venv/bin/activate
pip install -r requirement.txt
```

### ❌ **Port already in use**
**Solution:**
```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9  # Kill API on port 8000
lsof -ti:5173 | xargs kill -9  # Kill frontend on port 5173
```

### ❌ **Frontend won't connect to API**
**Problem:** Check CORS and WebSocket connection
**Solution:**
1. Verify backend is running: `curl http://localhost:8000/status`
2. Check frontend console for errors (F12 in browser)
3. Ensure both are running on correct ports (8000=API, 5173=frontend)

---

## **Development Workflow**

1. **Backend Development:**
   - Backend uses `--reload` flag for hot-reload
   - Edit `api/`, `core/`, `agents/` files
   - Changes auto-reload (check Terminal 1)

2. **Frontend Development:**
   - Frontend uses Vite hot-reload
   - Edit `frontend/src/` files  
   - Changes auto-update in browser

3. **Adding New Endpoints:**
   - Add route in `api/main.py`
   - Test with curl or test.sh
   - Update frontend to consume endpoint

4. **Database Changes:**
   - Modify models in `core/database.py`
   - Restart backend to apply schema
   - Database automatically migrates on startup

---

## **Monitoring the System**

### **Terminal Outputs**

**Backend Terminal:**
- Shows incoming API requests
- Logs agent activity (Alpha packet capture, Beta honeypots, Gamma policies)
- Displays database queries
- Shows WebSocket connections/disconnections

**Frontend Terminal:**
- Shows Vite compilation info
- Logs frontend build warnings
- Shows hot reload activity

**Test Terminal:**
- Shows HTTP status codes
- Confirms database persistence
- Validates data returned from endpoints

---

## **Next Steps**

### 📊 **View Real-Time Data:**
1. Start all three components (backend, frontend, tests)
2. Open http://localhost:5173 in your browser
3. Watch live alerts, traffic, and anomalies stream in

### 🔒 **Configure Security:**
1. Edit `.env` for risk thresholds
2. Modify policies in `core/policy_engine.py`
3. Adjust firewall rules in `system/firewall.py`

### 🚀 **Deploy Production:**
1. Use PostgreSQL instead of SQLite (set `DATABASE_URL`)
2. Run with proper process manager (systemd, supervisor)
3. Enable SSL/TLS for API
4. Deploy frontend with `npm run build`

---

## **Running Everything at Once (Alternative)**

If your system supports tmux or multiple terminals, here's a one-liner setup script:

```bash
#!/bin/bash
# Terminal 1: Backend
gnome-terminal --tab -t "Nemesis Backend" -e "bash -c 'cd /home/kali/Desktop/Nemesis && sudo ./start_backend.sh'"

# Wait for backend to start
sleep 5

# Terminal 2: Tests
gnome-terminal --tab -t "Nemesis Tests" -e "bash -c 'cd /home/kali/Desktop/Nemesis && source venv/bin/activate && python test_api.py'"

# Terminal 3: Frontend  
gnome-terminal --tab -t "Nemesis Frontend" -e "bash -c 'cd /home/kali/Desktop/Nemesis && ./start_frontend.sh'"
```

---

## **API Quick Reference**

```bash
# Get system status
curl http://localhost:8000/status

# Get all devices
curl http://localhost:8000/devices

# Get recent alerts
curl http://localhost:8000/alerts

# Get network traffic (last 50)
curl "http://localhost:8000/traffic?limit=50"

# Get honeypot detections
curl "http://localhost:8000/honeypots/detection?limit=50"

# Get anomalies
curl "http://localhost:8000/anomalies?limit=50"

# Interactive API docs
# Open: http://localhost:8000/docs
```

---

## **Key Files**

| File | Purpose |
|------|---------|
| `start_backend.sh` | Backend startup script |
| `start_frontend.sh` | Frontend startup script |
| `test.sh` | Quick test runner |
| `.env` | Configuration settings |
| `nemesis.db` | SQLite database (auto-created) |
| `api/main.py` | FastAPI application |
| `frontend/src/App.jsx` | React frontend |
| `core/database.py` | Database models & ORM |
| `core/orchestrator.py` | Agent orchestration |

---

**🎯 You're ready to go! Start with Terminal 1: `sudo ./start_backend.sh`**
