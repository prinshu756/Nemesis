# 🎛️ Backend System Monitor - Complete Implementation

## Overview

A comprehensive real-time monitoring dashboard that displays everything happening in the backend on the frontend. The Backend Monitor provides complete visibility into all system operations, agents, data, and database status.

---

## ✨ Features

### 1. **System Overview**
- 📊 CPU Usage (with visual progress bar)
- 💾 Memory Usage (with visual progress bar)
- 🟢 System Status (Running/Monitoring)

### 2. **Network Monitoring**
- 📱 Total Devices discovered
- ✅ Active Devices online
- 🚨 High-Risk Devices count
- 🔒 Isolated Devices count

### 3. **Alerts Dashboard**
- 🚨 Total Alerts
- 🔴 Critical Alerts
- 🟠 High Severity Alerts
- 🟡 Medium Severity Alerts
- 🟢 Low Severity Alerts

### 4. **Honeypot Management**
- 🍯 Active Honeypots count
- IP addresses of deployed honeypots
- Honeypot types and status

### 5. **Security Policies**
- 🛡️ Total Active Policies
- Policy details and configurations
- Policy status monitoring

### 6. **AI Agents Status**
- **Alpha Agent**: Network Discovery & Scanning
  - Real-time network scanning
  - Device discovery and identification
  - Status: Active/Inactive

- **Beta Agent**: Honeypot Deployment & Threat Capture
  - Honeypot management
  - Threat detection and capture
  - Status: Active/Inactive

- **Gamma Agent**: Adaptive Segmentation & Response
  - Network segmentation policies
  - Threat response and containment
  - Status: Active/Inactive

### 7. **Database Status**
- 📁 **Local SQLite Database**
  - Device count
  - Alert count
  - Traffic log count
  - Honeypot interaction count
  - Total records

- ☁️ **Neon PostgreSQL Database**
  - Connection status
  - Cloud availability indicator

### 8. **Recent Events**
- 📱 Latest discovered devices with IPs
- 🚨 Latest alerts with severity
- 📋 Total threats detected
- Risk scores and device types

---

## 🚀 How to Access

### From the Frontend

1. **Start Backend**
   ```bash
   python -m api.main
   ```

2. **Start Frontend**
   ```bash
   cd frontend && npm run dev
   ```

3. **Navigate to Backend Monitor**
   - Look for **🎛️ BACKEND** button in the sidebar
   - Click to view the comprehensive system monitor

### Direct API Access

```bash
# Get all backend status in JSON
curl http://localhost:8000/backend/status
```

---

## 📊 API Response Structure

```json
{
  "timestamp": 1696262400,
  "system": {
    "status": "running",
    "cpu_usage_percent": 45.2,
    "memory_usage_mb": 256.5,
    "uptime": "N/A"
  },
  "network_monitoring": {
    "total_devices": 42,
    "active_devices": 38,
    "high_risk_devices": 3,
    "devices_isolated": 1
  },
  "alerts": {
    "total_alerts": 15,
    "critical": 1,
    "high": 3,
    "medium": 5,
    "low": 6
  },
  "honeypots": {
    "active_count": 2,
    "honeypots": [
      {"ip": "192.168.1.100", "type": "cowrie"},
      {"ip": "192.168.1.101", "type": "dionaea"}
    ]
  },
  "security_policies": {
    "total_policies": 5,
    "policies": {...}
  },
  "agents": {
    "alpha": {
      "name": "Network Discovery & Scanning",
      "status": "active",
      "function": "Real-time network scanning and device discovery"
    },
    "beta": {
      "name": "Honeypot Deployment & Threat Capture",
      "status": "active",
      "function": "Deploy and manage honeypots for threat detection"
    },
    "gamma": {
      "name": "Adaptive Segmentation & Response",
      "status": "active",
      "function": "Implement segmentation policies and containment"
    }
  },
  "database": {
    "local": {
      "type": "SQLite",
      "devices": 42,
      "alerts": 15,
      "traffic_logs": 1250,
      "honeypot_interactions": 8,
      "total_records": 1315
    },
    "neon": {
      "type": "PostgreSQL Cloud",
      "status": "connected",
      "url": "***configured***"
    }
  },
  "recent_events": {
    "latest_devices": [...],
    "latest_alerts": [...],
    "total_threats_detected": 15
  }
}
```

---

## 🎨 Frontend Components

### Files Created

1. **BackendMonitor.jsx** - Main monitoring component
   - Real-time data fetching (every 2 seconds)
   - Expandable/collapsible sections
   - Color-coded severity indicators
   - Auto-refresh with status indicator

2. **BackendDashboard.jsx** - View wrapper
   - Integration with routing system
   - Full-screen display mode

3. **BackendMonitor.css** - Styling
   - Cyberpunk/hacker theme styling
   - Responsive grid layouts
   - Animated progress bars
   - Smooth transitions and hover effects

### Component Integration

```jsx
// App.jsx - Added to VIEWS
const VIEWS = {
  strat_map: StrategicMap,
  unit_stat: UnitStatus,
  threat_intel: ThreatIntel,
  diagnostics: Diagnostics,
  backend: BackendDashboard,  // ← NEW
};

// Sidebar.jsx - Added navigation item
{ id: 'backend', icon: '🎛️', label: 'BACKEND' }
```

---

## 🔄 Auto-Refresh Behavior

- **Data Fetch**: Every 2 seconds
- **Display Update**: Real-time
- **Status Indicator**: Bottom right corner shows "⟳ Auto-refreshing every 2 seconds"
- **No Manual Refresh**: Automatic polling keeps data current

---

## 🎯 Key Metrics Explained

### CPU Usage
- Shows percentage of CPU utilized by the backend
- Visual bar indicates usage level
- Helps identify performance issues

### Memory Usage
- Shows MB of RAM consumed
- Visual bar for quick reference
- Helps track memory leaks

### Device Metrics
- **Total Devices**: All discovered network devices
- **Active Devices**: Devices currently connected
- **High-Risk**: Devices with high or critical risk scores
- **Isolated**: Devices in quarantine/segmentation

### Alert Severity Levels
- 🔴 **Critical**: Requires immediate action
- 🟠 **High**: Significant security concern
- 🟡 **Medium**: Notable but not urgent
- 🟢 **Low**: Informational alerts

### Database Records
- Combined total of all persisted data
- Includes devices, alerts, traffic logs, honeypot interactions
- Growth indicator of system activity

---

## 🛠️ Technical Details

### Backend Endpoint

**Endpoint**: `GET /backend/status`

**Location**: `api/main.py`

**Features**:
- Pulls data from orchestrator (real-time)
- Queries SQLite database for record counts
- Collects system metrics (CPU, memory)
- Aggregates status from all agents
- Returns comprehensive JSON

### Frontend Component

**Path**: `frontend/src/components/BackendMonitor.jsx`

**Features**:
- Fetches data via fetch API
- 2-second auto-refresh interval
- Expandable sections (collapsible headers)
- Error handling and loading states
- Responsive grid layouts

---

## 📈 Use Cases

### 1. **System Health Monitoring**
- Monitor CPU and memory in real-time
- Identify performance bottlenecks
- Track when the system reaches saturation

### 2. **Security Threat Assessment**
- See critical alerts immediately
- Monitor high-risk device count
- Track honeypot interactions
- View isolated devices

### 3. **Network Inventory**
- Check total devices discovered
- Monitor active vs inactive devices
- Track device types and vendors
- View recent device discoveries

### 4. **Agent Performance**
- Verify all three agents are active
- Understand what each agent does
- Monitor their operational status

### 5. **Database Health**
- Verify data persistence
- Check record counts in each table
- Monitor database connectivity
- Ensure backup (Neon) is available

### 6. **Incident Response**
- Get immediate visual feedback on threats
- See which devices are isolated
- Verify honeypots are active
- Monitor alert patterns

---

## 🎨 Visual Design

### Color Scheme
- **Green (#00ff88)**: Normal/Good status
- **Orange (#ffaa00)**: Warning/Medium severity
- **Red (#ff4444, #ff0000)**: Critical/High severity
- **Cyan (#00ffaa)**: Highlight/Active
- **Dark Blue**: Background with gradient

### Typography
- **Monospace Font**: "Courier New" for that hacker aesthetic
- **Text Shadow**: Glowing effects for emphasis
- **Letter Spacing**: Increased for readability

### Layout
- **Collapsible Sections**: Click headers to expand/collapse
- **Grid System**: Responsive, adapts to screen size
- **Progress Bars**: Visual representation of metrics
- **Icon Badges**: Status indicators at a glance

---

## ⚙️ Configuration

### Update Frequency

To change the refresh interval, modify `BackendMonitor.jsx`:

```javascript
// Line ~25 - Change interval (milliseconds)
const interval = setInterval(fetchBackendStatus, 5000); // 5 seconds instead of 2
```

### Max Records Displayed

To change how many recent events are shown, modify `api/main.py`:

```python
# Line ~100 - Change slice limit
"latest_devices": list(orchestrator.state.devices.values())[:10]  # 10 instead of 5
```

---

## 🐛 Troubleshooting

### Backend Status Not Loading

**Problem**: Component shows error or "Loading" indefinitely

**Solution**:
1. Verify backend is running: `python -m api.main`
2. Check API response: `curl http://localhost:8000/backend/status`
3. Check browser console (F12) for errors
4. Verify `VITE_API_URL` in frontend .env

### CPU/Memory Not Showing

**Problem**: CPU and memory show 0

**Solution**:
1. Install psutil: `pip install psutil`
2. Restart backend
3. Check `api/main.py` has try/except for psutil import

### Database Counts Not Updating

**Problem**: Database record counts stay at 0

**Solution**:
1. Verify data has been saved: `sqlite3 nemesis.db "SELECT COUNT(*) FROM devices;"`
2. Check backend logs for database errors
3. Ensure `/db/devices` endpoint was called to save data

---

## 🔮 Future Enhancements

- [ ] Historical data graphing (time-series)
- [ ] Data export (CSV, JSON)
- [ ] Alert history/timeline
- [ ] Device drill-down details
- [ ] Custom alert thresholds
- [ ] Performance optimization recommendations
- [ ] System health scoring
- [ ] Trend analysis and predictions
- [ ] Multi-user dashboard (real-time sync)
- [ ] Mobile responsive improvements

---

## 📦 Installation

### 1. Backend Updates

The new endpoint is already in `api/main.py`. Ensure dependencies are installed:

```bash
pip install psutil
pip install sqlalchemy
```

### 2. Frontend Files

All frontend files are already created:
- `frontend/src/components/BackendMonitor.jsx`
- `frontend/src/css/BackendMonitor.css`
- `frontend/src/views/BackendDashboard.jsx`

### 3. Integration

Already integrated into:
- `frontend/src/App.jsx` - Added to VIEWS
- `frontend/src/components/Sidebar.jsx` - Added navigation item

---

## 🎓 Learning Resources

### Understanding the Dashboard

1. **System Section**: Shows backend resource usage
2. **Network Section**: Displays discovered devices
3. **Alerts Section**: Shows security notifications
4. **Honeypots Section**: Displays trap deployments
5. **Policies Section**: Shows segmentation rules
6. **Agents Section**: Shows AI system status
7. **Database Section**: Shows data persistence stats
8. **Events Section**: Shows recent discoveries and alerts

### Data Flow

```
Backend Orchestrator
    ↓
/backend/status Endpoint
    ↓
Frontend Fetch (every 2s)
    ↓
BackendMonitor Component
    ↓
Real-time Dashboard Display
```

---

## 📞 Support

For issues or questions:

1. Check browser console (F12 → Console)
2. Check backend logs (logs/nemesis.log)
3. Verify API response: `curl http://localhost:8000/backend/status`
4. Review this guide's troubleshooting section

---

## ✅ Verification Checklist

- [ ] Backend running: `python -m api.main`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Backend button visible in sidebar
- [ ] Click Backend button to view monitor
- [ ] Data displays and auto-refreshes
- [ ] System metrics show CPU and memory
- [ ] Device count updates
- [ ] Alert count updates
- [ ] Agent status shows as active
- [ ] Database counts show records
- [ ] Sections can expand/collapse

---

**Status**: ✅ **COMPLETE AND OPERATIONAL**

The Backend System Monitor is fully integrated and ready to use. Click 🎛️ **BACKEND** in the sidebar to start monitoring your Nemesis system in real-time!
