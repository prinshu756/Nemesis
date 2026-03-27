# Nemesis - AI-Powered Network Security System

Nemesis is an advanced Security Operations Center (SOC) platform that implements an OODA Loop (Observe, Orient, Decide, Act) architecture for automated network threat detection and response.

## 🏗️ Architecture

### Core Components
- **Agent Alpha**: Network device discovery and passive monitoring
- **Agent Beta**: Active deception through Docker-based honeypots
- **Agent Gamma**: Network enforcement with eBPF micro-segmentation
- **Risk Engine**: Multi-factor threat assessment with AI analysis
- **Orchestrator**: Async coordination of all agents

### Technology Stack
- **Backend**: Python 3.13, FastAPI, WebSocket
- **Frontend**: React 19, Vite, Modern CSS
- **AI/ML**: Sentence Transformers, FAISS vector search
- **Network**: Scapy, eBPF, Docker
- **Database**: In-memory with persistent logging

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Docker (optional, for honeypots)
- Linux with eBPF support (optional, for advanced filtering)

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirement.txt

# Start the API server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001
```

**API Endpoints:**
- `GET /` - System status
- `GET /devices` - Network devices
- `GET /alerts` - Security alerts
- `GET /status` - System status
- `GET /policies` - Segmentation policies
- `POST /devices/{mac}/isolate` - Isolate device
- `POST /devices/{mac}/honeypot` - Deploy honeypot
- `WebSocket /ws` - Real-time updates

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend URL:** http://localhost:5174

### 3. Full System

```bash
# Terminal 1: Backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 🎯 Features

### Network Monitoring
- **Passive Discovery**: ARP and IP packet analysis
- **Device Fingerprinting**: OS detection, TTL analysis, TCP window sizing
- **Real-time Updates**: WebSocket streaming to dashboard

### Threat Detection
- **Risk Assessment**: CVE-based vulnerability scoring
- **Behavioral Analysis**: Anomaly detection patterns
- **AI Integration**: Contextual threat analysis (Ollama support)

### Automated Response
- **Device Isolation**: Automatic network segmentation
- **Honeypot Deployment**: Docker container traps
- **Policy Enforcement**: eBPF-based traffic filtering

### Security Operations Center
- **Live Dashboard**: Real-time network visualization
- **Alert Management**: Prioritized threat notifications
- **System Monitoring**: Agent status and health checks

## 🔧 Configuration

### Core Settings (`core/config.py`)
```python
config = {
    'network': {
        'interface': 'eth0',
        'scan_interval': 30
    },
    'ai': {
        'use_local_ai': False,
        'ollama_url': 'http://localhost:11434',
        'model': 'llama2'
    },
    'ebpf': {
        'enabled': True
    },
    'honeypot': {
        'auto_deploy': True,
        'images': ['cowrie/cowrie:latest']
    }
}
```

### Environment Variables
- `NEMESIS_ENV`: development/production
- `OLLAMA_URL`: Local AI endpoint
- `DOCKER_HOST`: Docker daemon URL

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t nemesis-backend .
docker run -p 8001:8001 nemesis-backend
```

## 🔒 Security Considerations

### Permissions
- **Packet Capture**: Requires root or `cap_net_raw` capability
- **Docker Access**: User must be in docker group
- **eBPF**: Kernel must support eBPF (Linux 4.9+)

### Production Deployment
```bash
# Set capabilities for packet capture
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/python3

# Or run as root (not recommended)
sudo python -m uvicorn api.main:app --host 0.0.0.0 --port 8001
```

## 📊 Monitoring & Logs

### Log Files
- `logs/nemesis.log` - Main application logs
- `agents/alpha/logs/` - Network discovery logs
- `agents/beta/logs/` - Honeypot activity logs

### Health Checks
```bash
# System status
curl http://localhost:8001/status

# Device count
curl http://localhost:8001/devices | jq '.count'

# Active alerts
curl http://localhost:8001/alerts | jq 'length'
```

## 🔧 Development

### Project Structure
```
nemesis/
├── api/                 # FastAPI REST/WebSocket server
├── core/                # Core orchestration and configuration
├── agents/              # Alpha/Beta/Gamma agents
├── intelligence/        # AI and vector database
├── frontend/           # React dashboard
├── infra/              # Docker and deployment configs
└── system/             # System utilities
```

### Adding New Agents
1. Create agent class in `agents/`
2. Register with orchestrator in `core/orchestrator.py`
3. Add API endpoints in `api/main.py`
4. Update dashboard in `frontend/src/Dashboard.js`

### Testing
```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend && npm test

# Integration tests
python test_integration.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and authorized security testing purposes only. Users are responsible for complying with applicable laws and regulations. Unauthorized network monitoring may violate privacy laws and terms of service.

## 🆘 Troubleshooting

### Common Issues

**"Operation not permitted" for packet capture:**
```bash
# Grant network capabilities
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

**Docker permission denied:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

**eBPF not working:**
```bash
# Check kernel version
uname -r
# Should be 4.9+ for eBPF support
```

**Frontend WebSocket connection failed:**
- Ensure backend is running on port 8001
- Check CORS settings in `api/main.py`
- Verify firewall allows WebSocket connections

### Debug Mode
```bash
# Enable debug logging
export NEMESIS_ENV=development

# Run with verbose output
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --log-level debug
```

---

**Nemesis SOC** - Transforming network security through AI-driven automation.

### Agent Alpha (Detection)
- **Purpose**: Monitors network traffic and detects threats
- **Capabilities**:
  - Device fingerprinting (OS detection via TTL/TCP window)
  - VM detection (VirtualBox, VMware, etc.)
  - Device type spoofing detection
  - Suspicious port activity monitoring
  - High traffic anomaly detection
  - TTL pattern analysis

### Agent Gamma (Response)
- **Purpose**: Applies network filtering based on detected threats
- **Capabilities**:
  - IP address blocking
  - MAC address blocking
  - Micro-segmentation (allow only specific services)
  - Lateral movement prevention
  - eBPF-based XDP filtering (when available)

## Quick Start

### Prerequisites
```bash
# Install required packages
sudo apt update
sudo apt install -y python3-scapy clang llvm libbpf-dev

# Install Python dependencies
pip3 install scapy
```

### Run the Integrated System
```bash
cd /home/kali/Desktop/Nemesis
sudo python3 integrated_system.py
```

The system will:
1. Initialize both agents
2. Start network monitoring (if permissions allow)
3. Show automated responses

## Manual Testing

You can also test individual components:

### Test Agent Gamma Only
```bash
cd agents/gamma
python3 main.py
```

### Test Agent Alpha Only
```bash
cd agents/alpha
sudo python3 alpha.py
```

## Threat Types Detected

| Threat Type | Severity | Response |
|-------------|----------|----------|
| `vm_detected` | Medium | Micro-segmentation (DNS only) |
| `device_spoofing` | High | Complete isolation |
| `suspicious_ports` | High | Block lateral movement |
| `high_traffic` | Medium | Rate limiting |
| `ttl_anomaly` | Medium | Monitoring mode |

## Communication Flow

1. **Alpha** detects threats via packet analysis
2. **Alpha** calls registered threat callbacks
3. **Integrated System** converts Alpha threats to Gamma format
4. **Gamma's Decision Engine** processes threats
5. **Gamma** applies network filtering (blocks, segmentation)

## Customization

### Adding New Threat Types
Edit `agents/alpha/alpha.py` in the `detect_threats()` method.

### Modifying Responses
Edit `integrated_system.py` in the `convert_threat_format()` method.

### Custom Filtering Rules
Modify `agents/gamma/decision.py` and `agents/gamma/segmentation.py`.

## Project Structure

```
Nemesis/
├── integrated_system.py      # Main integration script
├── agents/
│   ├── alpha/
│   │   ├── alpha.py          # Threat detection agent
│   │   ├── test.py           # Placeholder
│   │   ├── data/             # Device fingerprints
│   │   └── logs/             # Packet logs, anomalies
│   └── gamma/
│       ├── gamma.py          # Network filtering agent
│       ├── gamma_ebpf.c      # eBPF filtering program
│       ├── main.py           # Gamma test script
│       ├── decision.py       # Threat decision engine
│       ├── segmentation.py   # Micro-segmentation logic
│       └── adaptive.py       # Adaptive defense
└── infra/                    # Docker/K8s configs
```

## Security Notes

- Requires root privileges for packet capture and eBPF loading
- eBPF filtering provides kernel-level performance
- Falls back gracefully when advanced features unavailable
- All actions are logged for audit purposes

## Troubleshooting

### "Operation not permitted" for packet capture
- Run with `sudo`
- System may not allow raw socket access in containers

### eBPF compilation fails
- Install `libbpf-dev` and `clang`
- Check `/usr/include/bpf/` exists

### Import errors
- Ensure all Python dependencies are installed
- Check Python path includes project root

## Next Steps

- Add persistent storage for threat intelligence
- Implement machine learning for anomaly detection
- Add alerting/notification system
- Create web dashboard for monitoring
- Add support for multiple network interfaces

## 🔧 Manual Testing

You can also test individual components:

### Test Agent Gamma Only
```bash
cd agents/gamma
python3 main.py
```

### Test Agent Alpha Only
```bash
cd agents/alpha
sudo python3 alpha.py
```

## 📊 Threat Types Detected

| Threat Type | Severity | Response |
|-------------|----------|----------|
| `vm_detected` | Medium | Micro-segmentation (DNS only) |
| `device_spoofing` | High | Complete isolation |
| `suspicious_ports` | High | Block lateral movement |
| `high_traffic` | Medium | Rate limiting |
| `ttl_anomaly` | Medium | Monitoring mode |

## 🔗 Communication Flow

1. **Alpha** detects threats via packet analysis
2. **Alpha** calls registered threat callbacks
3. **Integrated System** converts Alpha threats to Gamma format
4. **Gamma's Decision Engine** processes threats
5. **Gamma** applies network filtering (blocks, segmentation)

## 🛠️ Customization

### Adding New Threat Types
Edit `agents/alpha/alpha.py` in the `detect_threats()` method.

### Modifying Responses
Edit `integrated_system.py` in the `convert_threat_format()` method.

### Custom Filtering Rules
Modify `agents/gamma/decision.py` and `agents/gamma/segmentation.py`.

## 📁 Project Structure

```
Nemesis/
├── integrated_system.py      # Main integration script
├── agents/
│   ├── alpha/
│   │   ├── alpha.py          # Threat detection agent
│   │   ├── test.py           # Placeholder
│   │   ├── data/             # Device fingerprints
│   │   └── logs/             # Packet logs, anomalies
│   └── gamma/
│       ├── gamma.py          # Network filtering agent
│       ├── gamma_ebpf.c      # eBPF filtering program
│       ├── main.py           # Gamma test script
│       ├── decision.py       # Threat decision engine
│       ├── segmentation.py   # Micro-segmentation logic
│       └── adaptive.py       # Adaptive defense
└── infra/                    # Docker/K8s configs
```

## 🔒 Security Notes

- Requires root privileges for packet capture and eBPF loading
- eBPF filtering provides kernel-level performance
- Falls back gracefully when advanced features unavailable
- All actions are logged for audit purposes

## 🚨 Troubleshooting

### "Operation not permitted" for packet capture
- Run with `sudo`
- System may not allow raw socket access in containers

### eBPF compilation fails
- Install `libbpf-dev` and `clang`
- Check `/usr/include/bpf/` exists

### Import errors
- Ensure all Python dependencies are installed
- Check Python path includes project root

## 🎯 Next Steps

- Add persistent storage for threat intelligence
- Implement machine learning for anomaly detection
- Add alerting/notification system
- Create web dashboard for monitoring
- Add support for multiple network interfaces


If you run the project you have to run integrated_system.py
