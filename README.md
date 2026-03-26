# Threat Response System: Alpha + Gamma Integration

This system integrates **Agent Alpha** (threat detection) with **Agent Gamma** (network filtering) to create an automated threat response pipeline.

## Architecture

```
Network Traffic → Agent Alpha (Detection) → Threat Queue → Agent Gamma (Response) → Network Filtering
```

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
