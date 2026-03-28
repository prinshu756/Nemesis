# Nemesis SOC - Database Implementation & Data Capture Guide

## ✅ What's Been Implemented

### 1. **Database Layer** (`core/database.py`)
- **SQLAlchemy ORM** with SQLite database
- Tables for:
  - **Devices**: Network device tracking (MAC, IP, risk score, device type, etc.)
  - **Alerts**: Security alerts and anomalies
  - **TrafficLog**: Network traffic monitoring
  - **HoneypotInteraction**: Honeypot detection events  
  - **SystemMetric**: Performance and health metrics
  - **Vulnerability**: CVE tracking
  - **Configuration**: Dynamic system configuration

### 2. **Environment Configuration** (`.env` file)
- DATABASE_URL for SQLite or PostgreSQL
- Network monitoring settings
- API keys for external services
- Feature toggles (AI, eBPF, honeypots)

### 3. **API Endpoints** (`api/main.py`)
- `/status` - System status with database statistics
- `/alerts` - Retrieve alerts from database
- `/traffic` - Network traffic logs
- `/honeypots/detection` - Honeypot detection events
- `/anomalies` - Detected anomalies
- `/devices` - Device inventory
- `/devices/stats` - Device statistics

### 4. **Orchestrator Integration** (`core/orchestrator.py`)
Database methods:
- `store_device_data()` - Save device information
- `store_traffic_log()` - Log network traffic
- `store_honeypot_interaction()` - Record honeypot events
- `store_system_metric()` - Log system metrics
- `store_alert()` - Save security alerts
- `get_recent_alerts()` - Retrieve alerts from database
- `get_status()` - Get comprehensive system status

## 🚀 Running the Application

### Prerequisites
```bash
source venv/bin/activate
pip install -r requirement.txt
```

### Start the Server

**Without Root (Limited Network Capture):**
```bash
cd /home/kali/Desktop/Nemesis
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**With Root (Full Network Capture - Recommended):**
```bash
sudo su
cd /home/kali/Desktop/Nemesis
source venv/bin/activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Test API Endpoints
```bash
source venv/bin/activate
python test_api.py
```

## 📊 Data Capture Features

The application now captures and stores:

### 1. **Anomalies**
- Suspicious device behavior
- Unusual traffic patterns
- Statistical anomalies detected by Risk Engine
- Stored in: **Alerts** table

### 2. **Honeypot Detections**
- IP addresses attempting to connect to honeypots
- Attack type and threat classification
- Session logs and payloads
- Stored in: **HoneypotInteraction** table

### 3. **Network Traffic**
- Source/destination IPs and ports
- Protocol information
- Packet sizes and flags
- Traffic classification (normal/suspicious/malicious)
- Stored in: **TrafficLog** table

### 4. **High Traffic Detection**
- Traffic volume anomalies
- High packet count from specific IPs
- DDoS-like patterns
- Stored in: **TrafficLog** + **Alerts** tables

### 5. **Device Intelligence**
- Device type identification
- OS fingerprinting
- Port scanning results
- Risk scoring
- Stored in: **Device** table

## 📁 Database Structure

```
nemesis.db (SQLite)
├── devices (MAC, IP, risk details)
├── alerts (Anomalies, detections)
├── traffic_logs (Network packets)
├── honeypot_interactions (Attack logs)
├── system_metrics (Performance)
├── vulnerabilities (CVE data)
└── configurations (Dynamic config)
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Database
DATABASE_URL=sqlite:///./nemesis.db
# For PostgreSQL: postgresql://user:pass@localhost/nemesis

# Network
NETWORK_INTERFACE=eth0
PACKET_CAPTURE_ENABLED=true

# Risk Thresholds
RISK_THRESHOLD_LOW=20
RISK_THRESHOLD_MEDIUM=50
RISK_THRESHOLD_HIGH=80

# Features
HONEYPOT_ENABLED=true
EBPF_ENABLED=true
VECTOR_DB_ENABLED=true
```

## 📈 Querying Data

### Get Recent Alerts
```bash
curl http://localhost:8000/alerts?limit=50
```

### Get Traffic Logs
```bash
curl http://localhost:8000/traffic?limit=100
```

### Get Honeypot Detections
```bash
curl http://localhost:8000/honeypots/detection?limit=100
```

### Get Anomalies
```bash
curl http://localhost:8000/anomalies?limit=50
```

### Get System Status
```bash
curl http://localhost:8000/status
```

## 🔌 API Response Examples

### Alerts
```json
{
  "alerts": [
    {
      "id": 1,
      "level": "critical",
      "message": "High-risk device detected",
      "device_mac": "aa:bb:cc:dd:ee:ff",
      "risk_score": 85.5,
      "timestamp": "2026-03-28T14:35:08",
      "details": {...}
    }
  ]
}
```

### Traffic Logs
```json
{
  "traffic_logs": [
    {
      "id": 1,
      "source_ip": "192.168.1.100",
      "destination_ip": "192.168.1.1",
      "source_port": 54321,
      "destination_port": 80,
      "protocol": "TCP",
      "packet_size": 1024,
      "timestamp": "2026-03-28T14:35:08"
    }
  ]
}
```

###Honeypot Detections
```json
{
  "honeypot_detections": [
    {
      "id": 1,
      "ip_address": "203.0.113.45",
      "threat_type": "ssh",
      "attack_type": "brute_force",
      "honeypot_type": "cowrie",
      "severity": "high",
      "timestamp": "2026-03-28T14:35:08"
    }
  ]
}
```

## 🐛 Troubleshooting

### "Operation not permitted" (Network Capture)
**Solution:** Run with `sudo` for root privileges

### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

### Database locked
Database file might be corrupted. Backup and delete `nemesis.db`, it will be recreated.

### No data appearing in database
1. Check if network capture is running (check logs)
2. Verify packet capture interface is correct (see `.env`)
3. Run with `sudo` for full packet capture

## 📝 Next Steps

1. **Configure external data sources**
   - Add VirusTotal API key for threat intelligence
   - Configure Shodan API for device scanning
   - Set up webhooks for notifications

2. **Deploy Frontend**
   - Dashboard in `frontend/` directory
   - Uses React + Vite
   - Real-time WebSocket updates

3. **Scale to PostgreSQL**
   - Change `DATABASE_URL` in `.env`
   - Supports multiple concurrent connections
   - Better for large-scale deployments

4. **Add Custom Triggers**
   - Automate response actions
   - Data export/archival
   - Alert notifications

## ✨ Key Features

✅ Real-time threat detection
✅ Persistent data storage
✅ Network traffic analysis
✅ Honeypot integration
✅ Device profiling
✅ Risk scoring
✅ Anomaly detection
✅ RESTful API
✅ WebSocket support
✅ Configuration management
