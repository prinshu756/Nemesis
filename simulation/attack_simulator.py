"""
Attack Simulator — Generates realistic cyberattack scenarios.
Produces unpredictable, varied attack events that trigger the OODA loop.
"""

import random
import time
import uuid
from typing import Dict, List, Optional


# Attack scenario templates
ATTACK_SCENARIOS = [
    {
        "type": "port_scan",
        "name": "Sequential Port Scan",
        "severity": "medium",
        "description": "Sequential TCP SYN scan detected across {port_count} ports",
        "indicators": ["rapid_port_access", "syn_flood", "no_established_connections"],
        "target_ports": list(range(1, 1025)),
        "duration_range": (5, 30),
    },
    {
        "type": "port_scan",
        "name": "Stealth SYN Scan",
        "severity": "high",
        "description": "Stealth SYN scan detected — half-open connections on {port_count} ports",
        "indicators": ["half_open_conn", "randomized_ports", "low_rate"],
        "target_ports": [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080, 8443],
        "duration_range": (15, 60),
    },
    {
        "type": "brute_force",
        "name": "SSH Brute Force",
        "severity": "high",
        "description": "SSH brute force attack — {attempt_count} failed authentication attempts",
        "indicators": ["repeated_auth_failure", "credential_stuffing", "high_connection_rate"],
        "target_ports": [22],
        "credentials": [
            ("root", "admin"), ("root", "toor"), ("admin", "admin123"),
            ("user", "password"), ("root", "root"), ("admin", ""),
            ("pi", "raspberry"), ("ubnt", "ubnt"), ("admin", "1234"),
        ],
        "duration_range": (10, 120),
    },
    {
        "type": "brute_force",
        "name": "Telnet Credential Stuffing",
        "severity": "critical",
        "description": "Telnet brute force on IoT device — Mirai-style credential list detected",
        "indicators": ["iot_default_creds", "mirai_signature", "rapid_login"],
        "target_ports": [23],
        "credentials": [
            ("admin", "admin"), ("root", "vizxv"), ("root", "xc3511"),
            ("root", "888888"), ("root", "xmhdipc"), ("root", "default"),
            ("root", "juantech"), ("root", "123456"), ("root", "54321"),
            ("support", "support"), ("root", "root"),
        ],
        "duration_range": (5, 60),
    },
    {
        "type": "c2_beacon",
        "name": "C2 Beacon Pattern",
        "severity": "critical",
        "description": "Periodic C2 beacon detected — {beacon_interval}s interval to {c2_ip}",
        "indicators": ["periodic_outbound", "encrypted_payload", "non_standard_port"],
        "c2_servers": [
            "185.220.101.42", "91.219.236.87", "45.155.204.19",
            "194.26.192.71", "23.128.248.55", "103.75.201.4",
        ],
        "beacon_intervals": [30, 60, 120, 300],
        "duration_range": (60, 600),
    },
    {
        "type": "data_exfiltration",
        "name": "Data Exfiltration",
        "severity": "critical",
        "description": "Large outbound data transfer detected — {data_size}MB to external IP {dest_ip}",
        "indicators": ["large_outbound", "unusual_destination", "off_hours_transfer"],
        "dest_ips": ["45.33.32.156", "104.16.132.229", "198.51.100.42"],
        "data_sizes": [50, 150, 500, 1200, 3500],
        "duration_range": (30, 300),
    },
    {
        "type": "arp_spoof",
        "name": "ARP Spoofing",
        "severity": "high",
        "description": "ARP spoofing detected — MAC {spoof_mac} claiming gateway IP",
        "indicators": ["mac_ip_mismatch", "gratuitous_arp", "gateway_impersonation"],
        "duration_range": (5, 60),
    },
    {
        "type": "dns_tunneling",
        "name": "DNS Tunneling",
        "severity": "high",
        "description": "DNS tunneling detected — encoded payloads in TXT queries to {dns_domain}",
        "indicators": ["long_dns_queries", "high_entropy_subdomains", "txt_record_abuse"],
        "domains": ["x7k2m.evil.com", "data.exfil.net", "tunnel.c2server.org"],
        "duration_range": (60, 600),
    },
    {
        "type": "lateral_movement",
        "name": "Lateral Movement",
        "severity": "critical",
        "description": "Lateral movement detected — device scanning internal subnet {subnet}",
        "indicators": ["internal_scan", "smb_enum", "pass_the_hash"],
        "subnets": ["192.168.1.0/24", "10.0.1.0/24", "10.0.2.0/24", "172.16.5.0/24"],
        "target_ports": [445, 135, 139, 3389, 5985],
        "duration_range": (10, 120),
    },
    {
        "type": "firmware_exploit",
        "name": "Firmware Exploit Attempt",
        "severity": "critical",
        "description": "Exploit attempt targeting {device_type} firmware vulnerability {cve}",
        "indicators": ["malformed_http", "buffer_overflow_attempt", "firmware_upload"],
        "cves": [
            "CVE-2023-28771", "CVE-2023-33009", "CVE-2024-3400",
            "CVE-2023-20198", "CVE-2024-21762", "CVE-2023-46805",
        ],
        "duration_range": (5, 30),
    },
]

# Suspicious external IPs for realism
SUSPICIOUS_IPS = [
    {"ip": "185.220.101.42", "country": "RU", "org": "Unknown VPS Provider"},
    {"ip": "91.219.236.87", "country": "CN", "org": "Tencent Cloud"},
    {"ip": "45.155.204.19", "country": "IR", "org": "Unknown"},
    {"ip": "194.26.192.71", "country": "KP", "org": "Star JV"},
    {"ip": "23.128.248.55", "country": "US", "org": "Tor Exit Node"},
    {"ip": "103.75.201.4", "country": "VN", "org": "Unknown Hosting"},
    {"ip": "77.247.181.165", "country": "NL", "org": "Tor Exit Node"},
]


class AttackSimulator:
    """Generates realistic cyber attack events."""

    def __init__(self):
        self._attack_counter = 0
        self._active_attacks: Dict[str, dict] = {}
        self._attack_history: List[dict] = []

    def generate_attack(self, target_device: dict, scenario: Optional[dict] = None) -> dict:
        """Generate an attack event targeting a specific device."""
        if scenario is None:
            scenario = random.choice(ATTACK_SCENARIOS)

        self._attack_counter += 1
        attack_id = f"ATK-{self._attack_counter:04d}"
        source = random.choice(SUSPICIOUS_IPS)

        # Build attack specific details
        details = self._build_attack_details(scenario, target_device, source)

        attack = {
            "id": attack_id,
            "type": scenario["type"],
            "name": scenario["name"],
            "severity": scenario["severity"],
            "description": details["description"],
            "source_ip": source["ip"],
            "source_country": source["country"],
            "source_org": source["org"],
            "target_ip": target_device["ip"],
            "target_mac": target_device["mac"],
            "target_device": target_device["hostname"],
            "target_device_type": target_device["device_type"],
            "indicators": scenario["indicators"],
            "target_ports": details.get("ports", []),
            "timestamp": time.time(),
            "status": "active",
            "blocked": False,
            "response_action": None,
            "details": details,
        }

        self._active_attacks[attack_id] = attack
        self._attack_history.append(attack)

        return attack

    def _build_attack_details(self, scenario: dict, target: dict, source: dict) -> dict:
        """Build scenario-specific attack details."""
        details = {}
        attack_type = scenario["type"]

        if attack_type == "port_scan":
            port_count = random.randint(10, len(scenario.get("target_ports", [100])))
            ports = random.sample(scenario["target_ports"], min(port_count, len(scenario["target_ports"])))
            details["description"] = scenario["description"].format(port_count=port_count)
            details["ports"] = ports
            details["scan_rate"] = random.randint(50, 500)  # ports/sec

        elif attack_type == "brute_force":
            attempt_count = random.randint(50, 5000)
            creds = scenario.get("credentials", [("admin", "admin")])
            details["description"] = scenario["description"].format(attempt_count=attempt_count)
            details["ports"] = scenario["target_ports"]
            details["attempt_count"] = attempt_count
            details["credentials_tried"] = random.sample(creds, min(5, len(creds)))

        elif attack_type == "c2_beacon":
            c2_ip = random.choice(scenario.get("c2_servers", [source["ip"]]))
            interval = random.choice(scenario.get("beacon_intervals", [60]))
            details["description"] = scenario["description"].format(beacon_interval=interval, c2_ip=c2_ip)
            details["c2_server"] = c2_ip
            details["beacon_interval"] = interval
            details["encrypted"] = True

        elif attack_type == "data_exfiltration":
            dest_ip = random.choice(scenario.get("dest_ips", [source["ip"]]))
            data_size = random.choice(scenario.get("data_sizes", [100]))
            details["description"] = scenario["description"].format(data_size=data_size, dest_ip=dest_ip)
            details["data_size_mb"] = data_size
            details["destination_ip"] = dest_ip
            details["protocol"] = random.choice(["HTTPS", "DNS", "ICMP"])

        elif attack_type == "arp_spoof":
            spoof_mac = f"de:ad:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}"
            details["description"] = scenario["description"].format(spoof_mac=spoof_mac)
            details["spoofed_mac"] = spoof_mac
            details["gateway_ip"] = target["ip"].rsplit(".", 1)[0] + ".1"

        elif attack_type == "dns_tunneling":
            domain = random.choice(scenario.get("domains", ["evil.com"]))
            details["description"] = scenario["description"].format(dns_domain=domain)
            details["tunnel_domain"] = domain
            details["query_count"] = random.randint(100, 5000)

        elif attack_type == "lateral_movement":
            subnet = random.choice(scenario.get("subnets", ["192.168.1.0/24"]))
            details["description"] = scenario["description"].format(subnet=subnet)
            details["ports"] = scenario.get("target_ports", [445])
            details["target_subnet"] = subnet
            details["hosts_discovered"] = random.randint(5, 30)

        elif attack_type == "firmware_exploit":
            cve = random.choice(scenario.get("cves", ["CVE-2023-XXXXX"]))
            details["description"] = scenario["description"].format(
                device_type=target["device_type"], cve=cve
            )
            details["cve"] = cve
            details["exploit_payload_size"] = random.randint(200, 5000)

        else:
            details["description"] = scenario.get("description", "Unknown attack")

        return details

    def block_attack(self, attack_id: str) -> bool:
        """Mark an attack as blocked."""
        if attack_id in self._active_attacks:
            self._active_attacks[attack_id]["status"] = "blocked"
            self._active_attacks[attack_id]["blocked"] = True
            return True
        return False

    def get_active_attacks(self) -> List[dict]:
        """Get all active (unblocked) attacks."""
        return [a for a in self._active_attacks.values() if a["status"] == "active"]

    def get_attack_history(self, limit: int = 50) -> List[dict]:
        """Get attack history."""
        return self._attack_history[-limit:]
