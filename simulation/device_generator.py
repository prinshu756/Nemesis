"""
Device Generator — Realistic IoT device generation with proper fingerprinting.
Generates devices that look and behave like real network entities.
"""

import random
import time
import uuid
from typing import Dict, List, Optional

# Realistic device profiles with vendor MACs, OS, ports, behavioral patterns
DEVICE_PROFILES = [
    # IP Cameras
    {"type": "IP Camera", "vendor": "Hikvision", "mac_prefix": "c0:56:e3", "os": "Linux 3.18 (embedded)", "ports": [80, 443, 554, 8000], "traffic_pattern": "continuous_stream", "risk_base": 15},
    {"type": "IP Camera", "vendor": "Dahua", "mac_prefix": "3c:ef:8c", "os": "Linux 3.10 (embedded)", "ports": [80, 443, 554, 37777], "traffic_pattern": "continuous_stream", "risk_base": 15},
    {"type": "IP Camera", "vendor": "Axis", "mac_prefix": "ac:cc:8e", "os": "Linux 4.9 (AXIS OS)", "ports": [80, 443, 554], "traffic_pattern": "continuous_stream", "risk_base": 10},
    {"type": "IP Camera", "vendor": "Wyze", "mac_prefix": "2c:aa:8e", "os": "RTOS 2.1", "ports": [80, 443], "traffic_pattern": "burst", "risk_base": 20},

    # Smart Home
    {"type": "Smart Thermostat", "vendor": "Nest", "mac_prefix": "18:b4:30", "os": "ThreadOS 3.0", "ports": [443, 8443], "traffic_pattern": "periodic", "risk_base": 5},
    {"type": "Smart Speaker", "vendor": "Amazon", "mac_prefix": "fc:65:de", "os": "Fire OS 7", "ports": [443, 8443, 55443], "traffic_pattern": "burst", "risk_base": 8},
    {"type": "Smart Speaker", "vendor": "Google", "mac_prefix": "f4:f5:d8", "os": "Cast OS 1.56", "ports": [443, 8008, 8443], "traffic_pattern": "burst", "risk_base": 8},
    {"type": "Smart Lock", "vendor": "August", "mac_prefix": "d0:03:4b", "os": "Zephyr RTOS", "ports": [443], "traffic_pattern": "periodic", "risk_base": 25},
    {"type": "Smart Plug", "vendor": "TP-Link", "mac_prefix": "b0:a7:b9", "os": "Custom RTOS", "ports": [9999], "traffic_pattern": "periodic", "risk_base": 12},
    {"type": "Smart Light", "vendor": "Philips Hue", "mac_prefix": "00:17:88", "os": "Zigbee Stack", "ports": [80, 443], "traffic_pattern": "periodic", "risk_base": 5},
    {"type": "Smart Display", "vendor": "Samsung", "mac_prefix": "bc:72:b1", "os": "Tizen 6.5", "ports": [8001, 8002, 443], "traffic_pattern": "burst", "risk_base": 10},

    # Industrial IoT
    {"type": "PLC Controller", "vendor": "Siemens", "mac_prefix": "00:1b:1b", "os": "SIMATIC S7-1500", "ports": [102, 502, 80], "traffic_pattern": "continuous", "risk_base": 35},
    {"type": "SCADA Gateway", "vendor": "Schneider", "mac_prefix": "00:80:f4", "os": "SoMachine 4.3", "ports": [502, 44818, 80], "traffic_pattern": "continuous", "risk_base": 40},
    {"type": "RTU", "vendor": "ABB", "mac_prefix": "00:02:49", "os": "RTU560", "ports": [502, 2404, 80], "traffic_pattern": "periodic", "risk_base": 38},
    {"type": "HMI Panel", "vendor": "Rockwell", "mac_prefix": "00:00:bc", "os": "FactoryTalk 13", "ports": [44818, 2222, 80], "traffic_pattern": "burst", "risk_base": 30},

    # Medical Devices
    {"type": "Patient Monitor", "vendor": "Philips", "mac_prefix": "00:09:97", "os": "VxWorks 7.0", "ports": [80, 443, 2575], "traffic_pattern": "continuous_stream", "risk_base": 30},
    {"type": "Infusion Pump", "vendor": "Baxter", "mac_prefix": "00:1e:c9", "os": "QNX 7.1", "ports": [443, 2575], "traffic_pattern": "periodic", "risk_base": 35},
    {"type": "MRI Scanner", "vendor": "GE Healthcare", "mac_prefix": "00:19:fa", "os": "Linux 4.14 (RT)", "ports": [80, 443, 104, 2575], "traffic_pattern": "burst", "risk_base": 25},

    # Network Infrastructure
    {"type": "Router", "vendor": "Cisco", "mac_prefix": "00:1a:2b", "os": "IOS-XE 17.6", "ports": [22, 23, 80, 443, 161], "traffic_pattern": "continuous", "risk_base": 20},
    {"type": "Switch", "vendor": "Juniper", "mac_prefix": "88:e0:f3", "os": "Junos 22.2", "ports": [22, 830, 443], "traffic_pattern": "continuous", "risk_base": 15},
    {"type": "Access Point", "vendor": "Ubiquiti", "mac_prefix": "fc:ec:da", "os": "UniFi 7.x", "ports": [22, 443, 8443], "traffic_pattern": "continuous", "risk_base": 12},
    {"type": "Firewall", "vendor": "Fortinet", "mac_prefix": "00:09:0f", "os": "FortiOS 7.4", "ports": [22, 443, 541], "traffic_pattern": "continuous", "risk_base": 10},
    {"type": "NAS", "vendor": "Synology", "mac_prefix": "00:11:32", "os": "DSM 7.2", "ports": [22, 80, 443, 5000, 5001], "traffic_pattern": "burst", "risk_base": 15},

    # Workstations / Endpoints
    {"type": "Workstation", "vendor": "Dell", "mac_prefix": "f8:b1:56", "os": "Windows 11 Pro", "ports": [135, 139, 445, 3389], "traffic_pattern": "burst", "risk_base": 10},
    {"type": "Laptop", "vendor": "Lenovo", "mac_prefix": "e8:6a:64", "os": "Windows 11", "ports": [135, 445], "traffic_pattern": "burst", "risk_base": 8},
    {"type": "Laptop", "vendor": "Apple", "mac_prefix": "a8:66:7f", "os": "macOS 14.3", "ports": [22, 5900], "traffic_pattern": "burst", "risk_base": 5},
    {"type": "Server", "vendor": "HP", "mac_prefix": "94:18:82", "os": "Ubuntu 22.04 LTS", "ports": [22, 80, 443, 3306, 8080], "traffic_pattern": "continuous", "risk_base": 12},
    {"type": "Mobile", "vendor": "Samsung", "mac_prefix": "c0:ee:fb", "os": "Android 14", "ports": [443], "traffic_pattern": "burst", "risk_base": 5},

    # Suspicious / Rogue Devices
    {"type": "Unknown", "vendor": "Unknown", "mac_prefix": "02:00:00", "os": "Unknown", "ports": [4444, 5555, 8888], "traffic_pattern": "burst", "risk_base": 50},
    {"type": "Rogue AP", "vendor": "Unknown", "mac_prefix": "de:ad:be", "os": "OpenWrt", "ports": [22, 80, 443], "traffic_pattern": "continuous", "risk_base": 65},
]

# Subnet configurations for different network segments
NETWORK_SEGMENTS = {
    "iot": {"subnet": "10.0.1", "vlan": 10, "label": "IOT_SEGMENT"},
    "industrial": {"subnet": "10.0.2", "vlan": 20, "label": "ICS_SEGMENT"},
    "corporate": {"subnet": "192.168.1", "vlan": 30, "label": "CORP_SEGMENT"},
    "medical": {"subnet": "172.16.5", "vlan": 40, "label": "MED_SEGMENT"},
    "dmz": {"subnet": "10.10.0", "vlan": 50, "label": "DMZ_SEGMENT"},
}

# Hostnames that make devices feel real
HOSTNAME_PATTERNS = {
    "IP Camera": ["CAM-LOBBY-{n}", "CAM-PARKING-{n}", "CAM-ENTRANCE-{n}", "CAM-SERVER-RM-{n}", "CAM-HALLWAY-{n}"],
    "Smart Thermostat": ["HVAC-FLOOR{n}", "THERMO-CONF-{n}", "NEST-MAIN-{n}"],
    "Smart Speaker": ["ECHO-CONF-{n}", "GHOME-LOBBY-{n}", "ECHO-BREAK-{n}"],
    "Smart Lock": ["LOCK-MAIN-{n}", "LOCK-SERVER-{n}", "LOCK-REAR-{n}"],
    "PLC Controller": ["PLC-LINE-{n}", "PLC-ASSEMBLY-{n}", "PLC-PUMP-{n}"],
    "SCADA Gateway": ["SCADA-GW-{n}", "SCADA-PRIMARY-{n}"],
    "Patient Monitor": ["PMON-ICU-{n}", "PMON-ER-{n}", "PMON-OR-{n}"],
    "Infusion Pump": ["PUMP-ICU-{n}", "PUMP-ER-{n}"],
    "Router": ["RTR-CORE-{n}", "RTR-EDGE-{n}", "RTR-BRANCH-{n}"],
    "Switch": ["SW-FLOOR{n}", "SW-CORE-{n}", "SW-ACCESS-{n}"],
    "Firewall": ["FW-PERIMETER-{n}", "FW-INTERNAL-{n}"],
    "Workstation": ["WS-{n}", "PC-ADMIN-{n}", "PC-DEV-{n}"],
    "Laptop": ["LT-{n}", "MACBOOK-{n}", "THINKPAD-{n}"],
    "Server": ["SRV-WEB-{n}", "SRV-DB-{n}", "SRV-APP-{n}", "SRV-MAIL-{n}"],
    "NAS": ["NAS-PRIMARY-{n}", "NAS-BACKUP-{n}"],
    "Unknown": ["UNKNOWN-{n}", "ROGUE-{n}"],
    "Rogue AP": ["ROGUE-AP-{n}", "EVIL-TWIN-{n}"],
}


class DeviceGenerator:
    """Generates realistic IoT devices for the simulation."""

    def __init__(self):
        self._used_ips = set()
        self._used_macs = set()
        self._device_counter = 0
        self._hostname_counters = {}

    def generate_device(self, profile: Optional[dict] = None, segment: Optional[str] = None) -> dict:
        """Generate a single realistic device."""
        if profile is None:
            profile = random.choice(DEVICE_PROFILES)

        if segment is None:
            # Pick segment based on device type
            dev_type = profile["type"]
            if dev_type in ("PLC Controller", "SCADA Gateway", "RTU", "HMI Panel"):
                segment = "industrial"
            elif dev_type in ("Patient Monitor", "Infusion Pump", "MRI Scanner"):
                segment = "medical"
            elif dev_type in ("Workstation", "Laptop", "Server", "Mobile"):
                segment = "corporate"
            elif dev_type in ("Router", "Switch", "Firewall", "Access Point", "NAS"):
                segment = "corporate"
            elif dev_type in ("Unknown", "Rogue AP"):
                segment = random.choice(list(NETWORK_SEGMENTS.keys()))
            else:
                segment = "iot"

        net = NETWORK_SEGMENTS[segment]
        mac = self._generate_mac(profile["mac_prefix"])
        ip = self._generate_ip(net["subnet"])
        hostname = self._generate_hostname(profile["type"])
        self._device_counter += 1

        device = {
            "id": f"DEV-{self._device_counter:04d}",
            "mac": mac,
            "ip": ip,
            "hostname": hostname,
            "device_type": profile["type"],
            "vendor": profile["vendor"],
            "os_fingerprint": profile["os"],
            "ports": list(profile["ports"]),
            "segment": segment,
            "vlan": net["vlan"],
            "segment_label": net["label"],
            "risk_score": profile["risk_base"] + random.randint(-5, 15),
            "risk_level": "low",
            "status": "online",
            "isolation_status": "normal",
            "traffic_pattern": profile["traffic_pattern"],
            "packet_count": random.randint(100, 5000),
            "bytes_transferred": random.randint(10000, 5000000),
            "first_seen": time.time() - random.randint(0, 86400),
            "last_seen": time.time(),
            "health": random.randint(70, 100),
            "power_level": random.randint(60, 100),
            "temperature": round(random.uniform(28, 65), 1),
            "signal_strength": random.randint(-80, -20),
            "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
            "last_ping": round(random.uniform(0.1, 15.0), 2),
            "connection_count": random.randint(1, 50),
            "anomaly_score": round(random.uniform(0, 0.3), 3),
            "vm_detected": False,
            "coordinates": {
                "x": round(random.uniform(0.05, 0.95), 3),
                "y": round(random.uniform(0.05, 0.95), 3),
            },
        }

        # Calculate risk level
        rs = device["risk_score"]
        if rs >= 70:
            device["risk_level"] = "critical"
        elif rs >= 45:
            device["risk_level"] = "high"
        elif rs >= 20:
            device["risk_level"] = "medium"
        else:
            device["risk_level"] = "low"

        return device

    def generate_initial_fleet(self, count: int = 12) -> List[dict]:
        """Generate an initial fleet of devices for system startup."""
        devices = []
        # Ensure variety: pick from different categories
        categories = {
            "cameras": [p for p in DEVICE_PROFILES if p["type"] == "IP Camera"],
            "smart_home": [p for p in DEVICE_PROFILES if p["type"] in ("Smart Thermostat", "Smart Speaker", "Smart Lock", "Smart Plug", "Smart Light")],
            "industrial": [p for p in DEVICE_PROFILES if p["type"] in ("PLC Controller", "SCADA Gateway", "RTU", "HMI Panel")],
            "infrastructure": [p for p in DEVICE_PROFILES if p["type"] in ("Router", "Switch", "Access Point", "Firewall", "NAS")],
            "endpoints": [p for p in DEVICE_PROFILES if p["type"] in ("Workstation", "Laptop", "Server", "Mobile")],
        }

        # Distribute devices across categories
        per_category = max(1, count // len(categories))
        for cat_name, profiles in categories.items():
            for _ in range(min(per_category, len(profiles))):
                profile = random.choice(profiles)
                devices.append(self.generate_device(profile))

        # Fill remaining
        while len(devices) < count:
            devices.append(self.generate_device())

        return devices[:count]

    def generate_rogue_device(self) -> dict:
        """Generate a suspicious/rogue device for attack scenarios."""
        rogue_profiles = [p for p in DEVICE_PROFILES if p["type"] in ("Unknown", "Rogue AP")]
        profile = random.choice(rogue_profiles)
        device = self.generate_device(profile)
        device["risk_score"] = random.randint(55, 95)
        device["risk_level"] = "critical" if device["risk_score"] >= 70 else "high"
        device["anomaly_score"] = round(random.uniform(0.6, 1.0), 3)
        device["status"] = "suspicious"
        return device

    def _generate_mac(self, prefix: str) -> str:
        """Generate a unique MAC address with vendor prefix."""
        while True:
            suffix = ":".join(f"{random.randint(0, 255):02x}" for _ in range(3))
            mac = f"{prefix}:{suffix}"
            if mac not in self._used_macs:
                self._used_macs.add(mac)
                return mac

    def _generate_ip(self, subnet: str) -> str:
        """Generate a unique IP address in the given subnet."""
        while True:
            ip = f"{subnet}.{random.randint(2, 254)}"
            if ip not in self._used_ips:
                self._used_ips.add(ip)
                return ip

    def _generate_hostname(self, device_type: str) -> str:
        """Generate a realistic hostname."""
        patterns = HOSTNAME_PATTERNS.get(device_type, [f"{device_type.upper().replace(' ', '-')}-{{n}}"])
        if device_type not in self._hostname_counters:
            self._hostname_counters[device_type] = 0
        self._hostname_counters[device_type] += 1
        pattern = random.choice(patterns)
        return pattern.format(n=self._hostname_counters[device_type])
