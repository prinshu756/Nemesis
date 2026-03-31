"""
Agent Engine — Three intelligent agents (Alpha, Beta, Gamma) running as async simulation loops.
Implements the OODA loop with realistic inter-agent communication.
"""

import asyncio
import random
import time
from typing import Dict, List, Optional
from simulation.event_bus import (
    event_bus, Event,
    EVENT_DEVICE_DISCOVERED, EVENT_DEVICE_UPDATED, EVENT_THREAT_DETECTED,
    EVENT_ALERT_CREATED, EVENT_HONEYPOT_DEPLOYED, EVENT_HONEYPOT_INTERACTION,
    EVENT_DEVICE_ISOLATED, EVENT_DEVICE_RELEASED, EVENT_LOG_ENTRY,
    EVENT_AGENT_ACTION, EVENT_METRIC_UPDATE, EVENT_ATTACK_BLOCKED,
    STATE_MONITORING, STATE_ALERT, STATE_DEFENSE, STATE_LOCKDOWN,
)
from simulation.attack_simulator import AttackSimulator

# Log message templates for realistic output
ALPHA_LOG_MESSAGES = [
    "ARP_PROBE: Scanning subnet {subnet} for new hosts...",
    "FINGERPRINT: TCP/IP stack analysis on {ip} — OS identified: {os}",
    "PORT_SCAN: Service discovery on {ip} — {port_count} open ports detected",
    "TTL_CHECK: TTL analysis for {ip}: value={ttl}, stability={stability}",
    "MAC_VERIFY: Vendor lookup for {mac} — {vendor} confirmed",
    "BEACON_MON: Monitoring traffic pattern for {hostname} — {pattern} behavior",
    "ANOMALY_CHECK: Behavioral baseline comparison for {hostname} — score: {score}",
    "HANDSHAKE_ESTABLISHED: Secure link to {ip}... handshake success",
    "PACKET_SNIFFER: Detected encrypted uplink from {segment}",
]

BETA_LOG_MESSAGES = [
    "HONEYPOT_INIT: Deploying {pot_type} honeypot on {ip}:{port}",
    "HONEYPOT_ACTIVE: {pot_type} service emulation active — awaiting interaction",
    "LURE_DEPLOYED: Breadcrumb credentials injected into {hostname} ARP table",
    "INTERACTION_LOG: Attacker {src_ip} connected to honeypot {pot_id}",
    "CREDENTIAL_CAPTURE: Login attempt with {username}:{password} on {pot_type}",
    "SESSION_RECORD: Recording attacker session on honeypot {pot_id} — {duration}s",
    "TARPIT_ENGAGE: Slowing response to {src_ip} — tarpit mode active",
    "DECEPTION_UPDATE: Rotating honeypot signatures to avoid fingerprinting",
]

GAMMA_LOG_MESSAGES = [
    "ISOLATION: Device {mac} isolated — policy: {policy}",
    "FIREWALL_RULE: iptables -A FORWARD -s {ip} -j DROP — applied",
    "SEGMENT_UPDATE: VLAN {vlan} micro-segmentation rule updated",
    "BLOCK_IP: Blocking all traffic from {ip} — threat level: {level}",
    "BLOCK_MAC: MAC filter applied for {mac} on interface {iface}",
    "UNBLOCK: Device {mac} released from isolation — threat cleared",
    "POLICY_ENFORCE: Lateral movement blocked for {mac} — LAN access denied",
    "CONTAINMENT: Quarantine zone active for segment {segment}",
]

SYSTEM_LOG_MESSAGES = [
    "ENCRYPTION_LAYER: Re-established protocol_kappa",
    "SUBROUTINE_PING: Latency {latency}ms — DST: {ip}",
    "AUTO_THROTTLE: Core temp elevation — throttle engaged",
    "MEMORY_CHECK: Heap allocation nominal — {mem_used}% utilized",
    "QUANTUM_KEY: Key exchange cycle #{cycle} — hash verified",
    "COORD_LOCK: Satellite sync achieved — drift: {drift}ms",
    "SCANNING: SAT_COM feed for anomalies...",
    "TRACE_ROUTE: {src_ip} → {dst_ip} → [REDACTED]",
    "SECURE_CHANNEL: AES-4096-QUANTUM encryption active",
    "COUNTERMEASURE: Deploying countermeasures... node secured",
]


class AgentAlpha:
    """Discovery Agent — scans network, detects devices, fingerprints OS."""

    def __init__(self):
        self.name = "ALPHA"
        self.status = "active"
        self.scan_count = 0
        self.devices_discovered = 0
        self.last_scan_time = 0

    async def scan_cycle(self, devices: Dict[str, dict], device_generator, speed_multiplier: float = 1.0):
        """Run one scan cycle — may discover new device or update existing ones."""
        self.scan_count += 1
        self.last_scan_time = time.time()
        actions = []

        # Update existing device metrics
        for mac, device in list(devices.items()):
            if random.random() < 0.3:  # 30% chance to update each device per cycle
                device["packet_count"] += random.randint(10, 200)
                device["bytes_transferred"] += random.randint(1000, 50000)
                device["last_seen"] = time.time()
                device["last_ping"] = round(random.uniform(0.1, 15.0), 2)
                device["temperature"] = round(device["temperature"] + random.uniform(-0.5, 0.5), 1)
                device["temperature"] = max(25, min(85, device["temperature"]))

                # Occasional health fluctuation
                if random.random() < 0.1:
                    device["health"] = max(10, min(100, device["health"] + random.randint(-10, 5)))

                # Anomaly score drift
                device["anomaly_score"] = min(1.0, max(0, device["anomaly_score"] + random.uniform(-0.05, 0.03)))

                await event_bus.publish_new(EVENT_DEVICE_UPDATED, {
                    "mac": mac,
                    "device": device,
                }, source="agent_alpha")

        # Maybe discover a new device
        discover_chance = 0.15 * speed_multiplier
        if random.random() < discover_chance:
            new_device = device_generator.generate_device()
            devices[new_device["mac"]] = new_device
            self.devices_discovered += 1

            await event_bus.publish_new(EVENT_DEVICE_DISCOVERED, {
                "device": new_device,
            }, source="agent_alpha")

            # Log the discovery
            log_msg = random.choice(ALPHA_LOG_MESSAGES).format(
                subnet=new_device["ip"].rsplit(".", 1)[0] + ".0/24",
                ip=new_device["ip"],
                os=new_device["os_fingerprint"],
                port_count=len(new_device["ports"]),
                ttl=random.choice([64, 128, 255]),
                stability=round(random.uniform(0.7, 1.0), 2),
                mac=new_device["mac"],
                vendor=new_device["vendor"],
                hostname=new_device["hostname"],
                pattern=new_device["traffic_pattern"],
                score=round(new_device["anomaly_score"], 3),
                segment=new_device["segment_label"],
            )
            await event_bus.publish_new(EVENT_LOG_ENTRY, {
                "level": "INFO",
                "source": "ALPHA",
                "message": log_msg,
            }, source="agent_alpha")

            # Flag if suspicious
            if new_device["risk_score"] >= 45:
                await event_bus.publish_new(EVENT_ALERT_CREATED, {
                    "severity": "warning" if new_device["risk_score"] < 70 else "critical",
                    "title": f"Suspicious device detected: {new_device['hostname']}",
                    "message": f"Device {new_device['hostname']} ({new_device['ip']}) flagged — risk score: {new_device['risk_score']}",
                    "device_mac": new_device["mac"],
                    "device_ip": new_device["ip"],
                    "risk_score": new_device["risk_score"],
                }, source="agent_alpha")

            actions.append(("discovered", new_device))

        # Periodic system log
        if random.random() < 0.2:
            sys_log = random.choice(SYSTEM_LOG_MESSAGES).format(
                latency=random.randint(1, 50),
                ip=random.choice(list(devices.values()))["ip"] if devices else "0.0.0.0",
                mem_used=random.randint(40, 75),
                cycle=random.randint(1000, 9999),
                drift=round(random.uniform(0.001, 0.05), 4),
                src_ip=f"192.168.{random.randint(0,5)}.{random.randint(1,254)}",
                dst_ip=f"10.{random.randint(0,5)}.{random.randint(0,5)}.{random.randint(1,254)}",
            )
            await event_bus.publish_new(EVENT_LOG_ENTRY, {
                "level": random.choice(["INFO", "INFO", "INFO", "DEBUG"]),
                "source": "SYSTEM",
                "message": sys_log,
            }, source="system")

        return actions

    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "scan_count": self.scan_count,
            "devices_discovered": self.devices_discovered,
            "last_scan": self.last_scan_time,
        }


class AgentBeta:
    """Deception Agent — deploys honeypots, lures attackers."""

    def __init__(self):
        self.name = "BETA"
        self.status = "active"
        self.honeypots: Dict[str, dict] = {}
        self.honeypot_counter = 0
        self.interactions_logged = 0

    async def evaluate_threat(self, attack: dict, devices: Dict[str, dict]):
        """Evaluate a threat and decide whether to deploy honeypot."""
        severity = attack.get("severity", "low")
        attack_type = attack.get("type", "unknown")

        should_deploy = False
        pot_type = "generic"

        if attack_type == "brute_force":
            should_deploy = True
            pot_type = "ssh" if 22 in attack.get("target_ports", []) else "telnet"
        elif attack_type == "port_scan":
            should_deploy = severity in ("high", "critical")
            pot_type = "multi_service"
        elif attack_type == "c2_beacon":
            should_deploy = True
            pot_type = "c2_sinkhole"
        elif attack_type == "data_exfiltration":
            should_deploy = True
            pot_type = "data_trap"
        elif attack_type in ("lateral_movement", "firmware_exploit"):
            should_deploy = True
            pot_type = "iot_emulator"

        if should_deploy:
            await self.deploy_honeypot(
                attack["target_ip"],
                pot_type,
                attack["source_ip"],
                attack["id"],
            )

        return should_deploy

    async def deploy_honeypot(self, target_ip: str, pot_type: str, attacker_ip: str, attack_id: str):
        """Deploy a honeypot to lure an attacker."""
        self.honeypot_counter += 1
        pot_id = f"HP-{self.honeypot_counter:04d}"
        port = {"ssh": 22, "telnet": 23, "multi_service": 80, "c2_sinkhole": 443, "data_trap": 8080, "iot_emulator": 554, "generic": 9999}.get(pot_type, 9999)

        honeypot = {
            "id": pot_id,
            "type": pot_type,
            "target_ip": target_ip,
            "port": port,
            "attacker_ip": attacker_ip,
            "attack_id": attack_id,
            "deployed_at": time.time(),
            "status": "active",
            "interactions": 0,
            "last_interaction": None,
        }

        self.honeypots[pot_id] = honeypot

        await event_bus.publish_new(EVENT_HONEYPOT_DEPLOYED, {
            "honeypot": honeypot,
        }, source="agent_beta")

        # Log deployment
        log_msg = f"HONEYPOT_INIT: Deploying {pot_type} honeypot on {target_ip}:{port} — luring {attacker_ip}"
        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "INFO",
            "source": "BETA",
            "message": log_msg,
        }, source="agent_beta")

        # Simulate attacker interaction after a delay
        asyncio.create_task(self._simulate_interaction(pot_id, attacker_ip, pot_type))

        return pot_id

    async def _simulate_interaction(self, pot_id: str, attacker_ip: str, pot_type: str):
        """Simulate an attacker interacting with the honeypot."""
        await asyncio.sleep(random.uniform(3, 12))

        if pot_id not in self.honeypots or self.honeypots[pot_id]["status"] != "active":
            return

        self.interactions_logged += 1
        self.honeypots[pot_id]["interactions"] += 1
        self.honeypots[pot_id]["last_interaction"] = time.time()

        credentials = random.choice([
            ("root", "admin"), ("admin", "password123"),
            ("root", "toor"), ("user", "12345"),
        ])

        await event_bus.publish_new(EVENT_HONEYPOT_INTERACTION, {
            "honeypot_id": pot_id,
            "attacker_ip": attacker_ip,
            "pot_type": pot_type,
            "action": "credential_attempt",
            "username": credentials[0],
            "password": credentials[1],
        }, source="agent_beta")

        log_msg = f"CREDENTIAL_CAPTURE: {attacker_ip} attempted {credentials[0]}:{credentials[1]} on honeypot {pot_id}"
        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "WARNING",
            "source": "BETA",
            "message": log_msg,
        }, source="agent_beta")

    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "active_honeypots": len([h for h in self.honeypots.values() if h["status"] == "active"]),
            "total_deployed": self.honeypot_counter,
            "interactions_logged": self.interactions_logged,
        }


class AgentGamma:
    """Isolation Agent — enforces security, isolates threats."""

    def __init__(self):
        self.name = "GAMMA"
        self.status = "active"
        self.isolated_devices: Dict[str, dict] = {}
        self.actions_taken = 0
        self.rules_active = 0

    async def process_threat(self, attack: dict, devices: Dict[str, dict]):
        """Process a confirmed threat and take action."""
        severity = attack.get("severity", "low")
        target_mac = attack.get("target_mac")
        target_ip = attack.get("target_ip")
        source_ip = attack.get("source_ip")

        if severity == "critical":
            await self.isolate_device(target_mac, target_ip, "full_isolation", attack, devices)
        elif severity == "high":
            await self.isolate_device(target_mac, target_ip, "lateral_block", attack, devices)

        # Always block the attacker source
        self.actions_taken += 1
        self.rules_active += 1

        await event_bus.publish_new(EVENT_ATTACK_BLOCKED, {
            "attack_id": attack["id"],
            "source_ip": source_ip,
            "action": "blocked",
            "rule_type": "ip_block",
        }, source="agent_gamma")

        log_msg = f"BLOCK_IP: Blocking all traffic from {source_ip} — threat level: {severity.upper()}"
        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "CRITICAL",
            "source": "GAMMA",
            "message": log_msg,
        }, source="agent_gamma")

    async def isolate_device(self, mac: str, ip: str, policy: str, attack: dict, devices: Dict[str, dict]):
        """Isolate a compromised device."""
        if mac and mac in devices:
            devices[mac]["isolation_status"] = policy
            devices[mac]["status"] = "isolated"
            devices[mac]["risk_level"] = "critical"

        isolation = {
            "mac": mac,
            "ip": ip,
            "policy": policy,
            "attack_id": attack["id"],
            "isolated_at": time.time(),
            "reason": attack.get("description", "Threat detected"),
        }

        self.isolated_devices[mac or ip] = isolation
        self.actions_taken += 1

        await event_bus.publish_new(EVENT_DEVICE_ISOLATED, {
            "mac": mac,
            "ip": ip,
            "policy": policy,
            "reason": isolation["reason"],
            "attack_id": attack["id"],
        }, source="agent_gamma")

        log_msg = f"ISOLATION: Device {mac or ip} isolated — policy: {policy}"
        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "CRITICAL",
            "source": "GAMMA",
            "message": log_msg,
        }, source="agent_gamma")

        await event_bus.publish_new(EVENT_ALERT_CREATED, {
            "severity": "critical",
            "title": f"Device Isolated: {mac or ip}",
            "message": f"Device isolated with policy '{policy}' due to: {attack.get('name', 'threat')}",
            "device_mac": mac,
            "device_ip": ip,
        }, source="agent_gamma")

    async def release_device(self, identifier: str, devices: Dict[str, dict]):
        """Release a device from isolation."""
        if identifier in self.isolated_devices:
            iso = self.isolated_devices[identifier]
            mac = iso.get("mac")
            if mac and mac in devices:
                devices[mac]["isolation_status"] = "normal"
                devices[mac]["status"] = "online"
            del self.isolated_devices[identifier]
            self.rules_active = max(0, self.rules_active - 1)

            await event_bus.publish_new(EVENT_DEVICE_RELEASED, {
                "mac": mac,
                "ip": iso.get("ip"),
            }, source="agent_gamma")

            log_msg = f"UNBLOCK: Device {identifier} released from isolation — threat cleared"
            await event_bus.publish_new(EVENT_LOG_ENTRY, {
                "level": "INFO",
                "source": "GAMMA",
                "message": log_msg,
            }, source="agent_gamma")

            return True
        return False

    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "isolated_devices": len(self.isolated_devices),
            "actions_taken": self.actions_taken,
            "rules_active": self.rules_active,
        }
