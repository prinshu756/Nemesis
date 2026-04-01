# Backend-Frontend Database Integration Guide

## Overview

The Nemesis system now has a complete backend-frontend integration with dual database support:
- **Local SQLite** for development and caching
- **Neon PostgreSQL** for production cloud deployment

All discovered devices, alerts, traffic logs, and honeypot interactions are automatically persisted to both databases.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Components → useNemesisState → usePersistence       │   │
│  │                    ↓                                  │   │
│  │            API Service (api.js)                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                    ↓ HTTP/REST ↓                             │
├─────────────────────────────────────────────────────────────┤
│                  Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ API Endpoints (main.py)                              │   │
│  │   • Real-time data endpoints                         │   │
│  │   • Database persistence endpoints                   │   │
│  │   • Device action endpoints (isolate, honeypot)      │   │
│  │   • WebSocket for live updates                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                    ↓                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Database Service Layer (database_service.py)        │   │
│  │   • Dual DB synchronization                          │   │
│  │   • Session management                               │   │
│  │   • Error handling & fallbacks                       │   │
│  └──────────────────────────────────────────────────────┘   │
│        ↓ SQLAlchemy ORM ↓        ↓ SQLAlchemy ORM ↓          │
├─────────────────────────────────────────────────────────────┤
│         SQLite              │          Neon DB (PostgreSQL)  │
│    (Development/Local)      │     (Production/Cloud)         │
│    nemesis.db               │  ep-cool-bush-a5ygd1qx        │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

The system reads database configuration from `.env`:

```env
# Local SQLite Database (Development)
DATABASE_URL=sqlite:///./nemesis.db

# Neon PostgreSQL (Production)
NEON_DATABASE_URL=postgresql://user:password@ep-cool-bush-a5ygd1qx.us-east-1.aws.neon.tech/nemesis_prod?sslmode=require

# API Base URL
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### Real-Time Data Endpoints

Get current data from the running orchestrator:

```bash
# Get all devices from memory
GET /devices
# Response: { "devices": [...], "count": N }

# Get specific device
GET /devices/{mac}
# Response: { "mac": "...", "device": {...}, "risk_score": N, "risk_level": "..." }

# Get current alerts
GET /alerts
# Response: { "alerts": [...] }

# Get system status
GET /status
# Response: { "system_state": "...", "config": {...}, ... }

# Get traffic logs
GET /traffic?limit=100
# Response: { "traffic_logs": [...] }

# Get honeypot detections
GET /honeypots/detection?limit=100
# Response: { "honeypot_detections": [...] }

# Get anomalies
GET /anomalies?limit=100
# Response: { "anomalies": [...] }
```

### Database Persistence Endpoints

Save data to databases:

```bash
# Save all devices to database
POST /db/devices
# Response: { "message": "Saved X devices", "saved_count": X, "total_devices": N }

# Save single device to database
POST /db/device/{mac}
# Response: { "message": "Device saved", "mac": "...", "success": true }

# Save all alerts to database
POST /db/alerts
# Response: { "message": "Saved X alerts", "saved_count": X }

# Save single alert to database
POST /db/alert
# Body: { "message": "...", "severity": "medium", "type": "generic", "device_mac": "...", ... }

# Save traffic log to database
POST /db/traffic
# Body: { "source_ip": "...", "destination_ip": "...", "source_port": N, ..., }

# Save honeypot interaction to database
POST /db/honeypot-interaction
# Body: { "ip_address": "...", "threat_type": "...", "attack_type": "...", "honeypot_type": "...", ... }
```

### Database Retrieval Endpoints

Retrieve persisted data from databases:

```bash
# Get persisted devices
GET /db/devices?limit=100
# Response: { "devices": [...], "count": N, "source": "database" }

# Get persisted alerts
GET /db/alerts?limit=100
# Response: { "alerts": [...], "count": N, "source": "database" }

# Get persisted traffic logs
GET /db/traffic?limit=100
# Response: { "traffic_logs": [...], "count": N, "source": "database" }

# Get persisted honeypot interactions
GET /db/honeypot-interactions?limit=100
# Response: { "honeypot_interactions": [...], "count": N, "source": "database" }

# Get database status
GET /db/status
# Response: { "local_db": {...}, "neon_db": {...} }
```

### Device Action Endpoints

```bash
# Isolate a device
POST /devices/{mac}/isolate?policy=full_isolation
# Response: { "message": "Device isolated", "policy": "..." }

# Deploy honeypot for a device
POST /devices/{mac}/honeypot
# Response: { "message": "Honeypot deployed", "container": "...", "threat_type": "..." }
```

## Frontend Integration

### API Service Usage

The frontend has a comprehensive API service at `frontend/src/services/api.js`:

```javascript
import API from './services/api.js';

// Fetch real-time data
const devices = await API.getDevices();
const alerts = await API.getAlerts(50);
const status = await API.getSystemStatus();

// Save to database
await API.saveSingleDeviceToDatabase('aa:bb:cc:dd:ee:ff');
await API.saveAlertsToDatabase();

// Retrieve persisted data
const persistedDevices = await API.getPersistedDevices(100);
const persistedAlerts = await API.getPersistedAlerts(100);

// Device actions
await API.isolateDevice('aa:bb:cc:dd:ee:ff', 'full_isolation');
await API.deployHoneypot('aa:bb:cc:dd:ee:ff');

// Database management
const dbStatus = await API.getDatabaseStatus();
```

### Automatic Data Persistence

The frontend automatically syncs data to the database every 30 seconds through the `usePersistence` hook:

```javascript
import { useDataPersistence, loadPersistedData } from './hooks/usePersistence.jsx';

// In NemesisProvider component:
export function NemesisProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  // Load persisted data on mount
  useEffect(() => {
    loadPersistedData(dispatch);
  }, []);
  
  // Set up automatic syncing
  const { syncToDatabase } = useDataPersistence(dispatch, state);
  
  // ... rest of provider
}
```

### Bulk State Updates

New action types support bulk device and alert updates:

```javascript
// Bulk update devices from API response
dispatch({
  type: 'BULK_UPDATE_DEVICES',
  payload: response.devices // Array of device objects
});

// Bulk update alerts
dispatch({
  type: 'BULK_UPDATE_ALERTS',
  payload: response.alerts // Array of alert objects
});
```

## Data Synchronization Flow

1. **On Frontend Load:**
   - Page loads → NemesisProvider initializes
   - `loadPersistedData()` fetches historical data from database
   - Redux state populated with persisted data
   - WebSocket connects for real-time updates

2. **During Operation:**
   - New devices discovered/updated → Redux state updated
   - New alerts created → Redux state updated
   - WebSocket broadcasts events in real-time
   - API fetches refresh every 5 seconds

3. **Periodic Sync (Every 30 seconds):**
   - Check if new devices exist in state
   - POST all devices to `/db/devices`
   - POST all alerts to `/db/alerts`
   - System logs show sync status

4. **Database Persistence:**
   - Local SQLite updates immediately
   - Neon DB updates in parallel (failures logged)
   - Both databases maintain consistency
   - No data loss if one DB fails

## Database Models

### Device
```python
{
  'id': int,
  'mac_address': str,
  'ip_address': str,
  'hostname': str,
  'device_type': str,
  'vendor': str,
  'risk_score': float,
  'risk_level': str,  # low, medium, high, critical
  'threat_level': str,
  'packet_count': int,
  'bytes_transferred': int,
  'first_seen': datetime,
  'last_seen': datetime,
  'is_active': bool,
  'isolation_status': str,
  'ports': dict,
  'services': dict
}
```

### Alert
```python
{
  'id': int,
  'message': str,
  'severity': str,  # low, medium, high, critical
  'alert_type': str,
  'device_mac': str,
  'status': str,  # open, acknowledged, resolved
  'details': dict,
  'timestamp': datetime
}
```

### TrafficLog
```python
{
  'id': int,
  'source_ip': str,
  'destination_ip': str,
  'source_port': int,
  'destination_port': int,
  'protocol': str,
  'packet_size': int,
  'device_id': int,
  'timestamp': datetime
}
```

### HoneypotInteraction
```python
{
  'id': int,
  'ip_address': str,
  'threat_type': str,
  'attack_type': str,
  'honeypot_type': str,
  'severity': str,
  'details': dict,
  'timestamp': datetime
}
```

## Running the System

### Start Backend
```bash
# Terminal 1 - Backend API
cd /home/kali/Desktop/Nemesis
source venv/bin/activate
python -m api.main
# Server runs at http://localhost:8000
```

### Start Frontend
```bash
# Terminal 2 - Frontend Dev Server
cd /home/kali/Desktop/Nemesis/frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

### Monitor Databases
```bash
# Check local SQLite
sqlite3 nemesis.db ".tables"
sqlite3 nemesis.db "SELECT COUNT(*) FROM devices;"

# Check Neon DB (via psql)
psql postgresql://user:password@ep-cool-bush-a5ygd1qx.us-east-1.aws.neon.tech/nemesis_prod
# \d (list tables)
# SELECT COUNT(*) FROM devices;
```

## Troubleshooting

### Database Connection Issues

```bash
# Test local SQLite
python -c "from core.database import DatabaseManager; db = DatabaseManager(); db.init_database(); print('SQLite OK')"

# Test Neon DB
python -c "from core.database import DatabaseManager; db = DatabaseManager('postgresql://...'); db.init_database(); print('Neon OK')"
```

### API Connection Issues

```bash
# Check backend is running
curl http://localhost:8000/

# Check specific endpoint
curl http://localhost:8000/devices
curl http://localhost:8000/db/status

# Check frontend environment
cat frontend/.env
```

### Data Not Syncing

1. Check browser console for API errors
2. Verify `VITE_API_URL` in frontend/.env
3. Verify `DATABASE_URL` in backend .env
4. Check backend logs for database errors
5. Ensure both databases are accessible

### Performance Optimization

If experiencing slow syncs:
- Reduce `MAX_ALERTS` constant (currently 100)
- Increase `SYNC_INTERVAL` in `usePersistence.jsx` (currently 30s)
- Implement pagination in database queries
- Add database indexing for frequently queried fields

## Security Considerations

1. **Production Deployment:**
   - Never expose `NEON_DATABASE_URL` in frontend code
   - Use environment variables only for backend
   - Implement API authentication/authorization
   - Enable CORS restrictions

2. **Database Access:**
   - Use connection pooling for PostgreSQL
   - Parameterize all queries (SQLAlchemy handles this)
   - Regular database backups
   - Enable SSL/TLS for remote connections

3. **API Security:**
   - Add rate limiting on persistence endpoints
   - Implement request validation
   - Add API key authentication
   - Log all data modifications

## Future Enhancements

- [ ] Real-time WebSocket data persistence
- [ ] GraphQL API for more efficient queries
- [ ] Database compression/archival
- [ ] Full-text search on alerts and logs
- [ ] Data export (CSV/JSON)
- [ ] Advanced filtering and querying
- [ ] Time-series data visualization
- [ ] Automated data cleanup policies
