"""
Simulation Engine — Main orchestrator for the smart simulation system.
Runs continuous async loops that generate realistic cybersecurity events.
Supports configurable speed modes: realistic, demo, custom.
"""

import asyncio
import random
import time
import math
from typing import Dict, List, Optional

from simulation.event_bus import (
    event_bus, Event,
    EVENT_DEVICE_DISCOVERED, EVENT_THREAT_DETECTED, EVENT_LOG_ENTRY,
    EVENT_METRIC_UPDATE, EVENT_AGENT_ACTION, EVENT_ATTACK_STARTED,
    EVENT_NETWORK_MAP_UPDATE, EVENT_ALERT_CREATED,
    STATE_MONITORING, STATE_ALERT, STATE_DEFENSE, STATE_LOCKDOWN,
)
from simulation.device_generator import DeviceGenerator
from simulation.attack_simulator import AttackSimulator
from simulation.agent_engine import AgentAlpha, AgentBeta, AgentGamma


# Speed presets (multiplier for timing)
SPEED_PRESETS = {
    "realistic": {
        "device_scan_interval": (8, 20),     # seconds between scans
        "attack_interval": (30, 120),         # seconds between attacks
        "metric_interval": 5,                  # seconds between metric updates
        "alpha_cycle": 4,                      # seconds between Alpha cycles
        "speed_multiplier": 0.5,
    },
    "demo": {
        "device_scan_interval": (3, 8),
        "attack_interval": (10, 35),
        "metric_interval": 2,
        "alpha_cycle": 2,
        "speed_multiplier": 1.5,
    },
    "fast": {
        "device_scan_interval": (1, 3),
        "attack_interval": (5, 15),
        "metric_interval": 1,
        "alpha_cycle": 1,
        "speed_multiplier": 3.0,
    },
}


class SimulationEngine:
    """Main simulation orchestrator."""

    def __init__(self, speed_mode: str = "demo"):
        self.speed_mode = speed_mode
        self.speed_config = SPEED_PRESETS.get(speed_mode, SPEED_PRESETS["demo"])
        self.custom_speed: float = 1.0  # For custom slider (0.1 to 5.0)

        # Sub-systems
        self.device_generator = DeviceGenerator()
        self.attack_simulator = AttackSimulator()
        self.agent_alpha = AgentAlpha()
        self.agent_beta = AgentBeta()
        self.agent_gamma = AgentGamma()

        # State
        self.devices: Dict[str, dict] = {}
        self.running = False
        self.start_time = 0
        self.cycle_count = 0

        # Metrics tracking
        self._cpu_usage = 42.0
        self._memory_used = 52.0
        self._network_throughput = 1.2  # Gbps
        self._temperature = 54.0
        self._power_status = "STABLE"
        self._storage_used = 842  # TB

    @property
    def speed_multiplier(self):
        if self.speed_mode == "custom":
            return self.custom_speed
        return self.speed_config["speed_multiplier"]

    def set_speed(self, mode: str = None, custom_value: float = None):
        """Change simulation speed."""
        if mode and mode in SPEED_PRESETS:
            self.speed_mode = mode
            self.speed_config = SPEED_PRESETS[mode]
        elif custom_value is not None:
            self.speed_mode = "custom"
            self.custom_speed = max(0.1, min(5.0, custom_value))

    async def start(self):
        """Start all simulation loops."""
        self.running = True
        self.start_time = time.time()

        # Start event bus
        await event_bus.start()

        # Generate initial fleet
        initial = self.device_generator.generate_initial_fleet(count=14)
        for dev in initial:
            self.devices[dev["mac"]] = dev

        # Announce initial devices
        for dev in initial:
            await event_bus.publish_new(EVENT_DEVICE_DISCOVERED, {
                "device": dev,
            }, source="agent_alpha")

        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "INFO",
            "source": "SYSTEM",
            "message": f"NEMESIS_INIT: System online — {len(initial)} devices discovered on startup",
        }, source="system")

        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "INFO",
            "source": "SYSTEM",
            "message": "SECURE_LINK: Established... handshake success",
        }, source="system")

        # Launch all loops as concurrent tasks
        tasks = [
            asyncio.create_task(self._alpha_loop()),
            asyncio.create_task(self._attack_loop()),
            asyncio.create_task(self._metrics_loop()),
            asyncio.create_task(self._network_map_loop()),
            asyncio.create_task(self._system_log_loop()),
        ]

        # Don't await — let them run in background
        return tasks

    def stop(self):
        """Stop all simulation loops."""
        self.running = False
        event_bus.stop()

    # ─── ALPHA CYCLE ─────────────────────────────────────────────────────

    async def _alpha_loop(self):
        """Alpha agent continuous scanning loop."""
        while self.running:
            try:
                interval = self.speed_config["alpha_cycle"] / self.speed_multiplier
                await asyncio.sleep(max(0.5, interval))

                await self.agent_alpha.scan_cycle(
                    self.devices,
                    self.device_generator,
                    self.speed_multiplier,
                )
                self.cycle_count += 1

            except Exception as e:
                print(f"[SimEngine] Alpha loop error: {e}")
                await asyncio.sleep(2)

    # ─── ATTACK SIMULATION LOOP ──────────────────────────────────────────

    async def _attack_loop(self):
        """Periodically generate attack events."""
        # Wait before first attack
        await asyncio.sleep(random.uniform(5, 15) / self.speed_multiplier)

        while self.running:
            try:
                interval = random.uniform(*self.speed_config["attack_interval"]) / self.speed_multiplier
                await asyncio.sleep(max(2, interval))

                if not self.devices:
                    continue

                # Pick a target device (bias toward higher-risk devices)
                device_list = list(self.devices.values())
                weights = [max(1, d.get("risk_score", 10)) for d in device_list]
                target = random.choices(device_list, weights=weights, k=1)[0]

                # Generate attack
                attack = self.attack_simulator.generate_attack(target)

                await event_bus.publish_new(EVENT_ATTACK_STARTED, {
                    "attack": attack,
                }, source="attack_simulator")

                await event_bus.publish_new(EVENT_THREAT_DETECTED, {
                    "attack_id": attack["id"],
                    "type": attack["type"],
                    "name": attack["name"],
                    "severity": attack["severity"],
                    "description": attack["description"],
                    "source_ip": attack["source_ip"],
                    "target_ip": attack["target_ip"],
                    "target_mac": attack["target_mac"],
                    "target_device": attack["target_device"],
                }, source="threat_detection")

                # Log the threat
                await event_bus.publish_new(EVENT_LOG_ENTRY, {
                    "level": "CRITICAL" if attack["severity"] == "critical" else "WARNING",
                    "source": "THREAT_ENGINE",
                    "message": f"WARNING: {attack['name']} detected on {attack['target_device']} — source: {attack['source_ip']}",
                }, source="threat_detection")

                # Update target device risk
                if target["mac"] in self.devices:
                    risk_boost = {"low": 5, "medium": 15, "high": 25, "critical": 40}.get(attack["severity"], 10)
                    self.devices[target["mac"]]["risk_score"] = min(100, self.devices[target["mac"]]["risk_score"] + risk_boost)
                    self.devices[target["mac"]]["anomaly_score"] = min(1.0, self.devices[target["mac"]]["anomaly_score"] + 0.2)
                    rs = self.devices[target["mac"]]["risk_score"]
                    self.devices[target["mac"]]["risk_level"] = (
                        "critical" if rs >= 70 else "high" if rs >= 45 else "medium" if rs >= 20 else "low"
                    )

                # OODA: Beta evaluates (Decide)
                honeypot_deployed = await self.agent_beta.evaluate_threat(attack, self.devices)

                # OODA: Gamma acts (Act)
                if attack["severity"] in ("high", "critical"):
                    await self.agent_gamma.process_threat(attack, self.devices)
                    self.attack_simulator.block_attack(attack["id"])

                # Create alert
                await event_bus.publish_new(EVENT_ALERT_CREATED, {
                    "severity": attack["severity"],
                    "title": attack["name"],
                    "message": attack["description"],
                    "source_ip": attack["source_ip"],
                    "target_ip": attack["target_ip"],
                    "device_mac": attack["target_mac"],
                    "attack_type": attack["type"],
                    "honeypot_deployed": honeypot_deployed,
                }, source="ooda_loop")

            except Exception as e:
                print(f"[SimEngine] Attack loop error: {e}")
                await asyncio.sleep(5)

    # ─── METRICS LOOP ────────────────────────────────────────────────────

    async def _metrics_loop(self):
        """Generate system metrics for diagnostics view."""
        while self.running:
            try:
                interval = self.speed_config["metric_interval"]
                await asyncio.sleep(interval)

                # Simulate fluctuating metrics
                self._cpu_usage = max(10, min(95, self._cpu_usage + random.uniform(-5, 5)))
                self._memory_used = max(30, min(90, self._memory_used + random.uniform(-2, 2)))
                self._temperature = max(35, min(80, self._temperature + random.uniform(-1, 1)))
                self._network_throughput = max(0.1, min(10, self._network_throughput + random.uniform(-0.3, 0.3)))

                # CPU per-core metrics (8 cores)
                cpu_cores = []
                for i in range(8):
                    core_usage = max(5, min(100, self._cpu_usage + random.uniform(-20, 20)))
                    cpu_cores.append(round(core_usage, 1))

                metrics = {
                    "cpu_usage": round(self._cpu_usage, 1),
                    "cpu_cores": cpu_cores,
                    "memory_used": round(self._memory_used, 1),
                    "memory_total_gb": 16.4,
                    "temperature": round(self._temperature, 1),
                    "network_throughput_gbps": round(self._network_throughput, 2),
                    "storage_used_tb": self._storage_used,
                    "storage_total_tb": 1200,
                    "power_status": self._power_status,
                    "power_level": random.randint(95, 100),
                    "thermal_status": "WARNING" if self._temperature > 65 else "NOMINAL",
                    "uptime_seconds": int(time.time() - self.start_time),
                    "total_devices": len(self.devices),
                    "active_threats": len(self.attack_simulator.get_active_attacks()),
                    "total_packets": sum(d.get("packet_count", 0) for d in self.devices.values()),
                    "ooda_latency_ms": round(random.uniform(8, 45), 1),
                    "signal_strength": "SECURE_SAT_LINK",
                    "encryption": "AES-4096-QUANTUM",
                }

                await event_bus.publish_new(EVENT_METRIC_UPDATE, metrics, source="system_monitor")

            except Exception as e:
                print(f"[SimEngine] Metrics loop error: {e}")
                await asyncio.sleep(5)

    # ─── NETWORK MAP LOOP ────────────────────────────────────────────────

    async def _network_map_loop(self):
        """Periodically push network topology updates."""
        while self.running:
            try:
                await asyncio.sleep(3)

                # Build connections between devices
                connections = []
                device_list = list(self.devices.values())
                if len(device_list) >= 2:
                    # Create hub-and-spoke connections from routers/switches
                    infra = [d for d in device_list if d["device_type"] in ("Router", "Switch", "Firewall", "Access Point")]
                    others = [d for d in device_list if d["device_type"] not in ("Router", "Switch", "Firewall", "Access Point")]

                    for inf in infra:
                        # Connect to 3-6 other devices
                        connected = random.sample(others, min(random.randint(3, 6), len(others)))
                        for dev in connected:
                            connections.append({
                                "source": inf["mac"],
                                "target": dev["mac"],
                                "bandwidth": random.randint(10, 1000),
                                "latency": round(random.uniform(0.5, 15), 1),
                                "status": "active" if dev["isolation_status"] == "normal" else "blocked",
                            })

                map_data = {
                    "devices": [
                        {
                            "mac": d["mac"],
                            "ip": d["ip"],
                            "hostname": d["hostname"],
                            "type": d["device_type"],
                            "status": d["status"],
                            "risk_level": d["risk_level"],
                            "isolation": d["isolation_status"],
                            "x": d["coordinates"]["x"],
                            "y": d["coordinates"]["y"],
                            "segment": d["segment_label"],
                        } for d in device_list
                    ],
                    "connections": connections,
                }

                await event_bus.publish_new(EVENT_NETWORK_MAP_UPDATE, map_data, source="network_mapper")

            except Exception as e:
                print(f"[SimEngine] Network map loop error: {e}")
                await asyncio.sleep(5)

    # ─── SYSTEM LOG LOOP ─────────────────────────────────────────────────

    async def _system_log_loop(self):
        """Generate ambient system log messages for realism."""
        while self.running:
            try:
                await asyncio.sleep(random.uniform(2, 6) / self.speed_multiplier)

                log_templates = [
                    ("INFO", "SYSTEM", "HANDSHAKE_INITIATED: SECTOR_{sector}_UPLINK"),
                    ("INFO", "SYSTEM", "ENCRYPTION_LAYER: Re-established PROTOCOL_KAPPA"),
                    ("DEBUG", "SYSTEM", "SUBROUTINE_PING: Latency {latency}ms"),
                    ("INFO", "SYSTEM", "AUTO_THROTTLE_ENGAGED: Core temp nominal"),
                    ("INFO", "SYSTEM", "SCANNING: SAT_COM feed for anomalies..."),
                    ("DEBUG", "SYSTEM", "COORD_LOCK: Satellite sync — drift: {drift}ms"),
                    ("INFO", "ALPHA", "BEACON_MON: Traffic pattern analysis in progress..."),
                    ("INFO", "SYSTEM", "QUANTUM_KEY: Exchange cycle #{cycle} — hash verified"),
                    ("INFO", "SYSTEM", "SECURE_CHANNEL: AES-4096-QUANTUM encryption active"),
                    ("DEBUG", "SYSTEM", "MEMORY_CHECK: Heap allocation nominal — {mem}% utilized"),
                ]

                level, source, template = random.choice(log_templates)
                message = template.format(
                    sector=f"{random.randint(1,9)}{chr(random.randint(65,72))}",
                    latency=random.randint(1, 50),
                    drift=round(random.uniform(0.001, 0.05), 4),
                    cycle=random.randint(1000, 9999),
                    mem=random.randint(40, 75),
                )

                await event_bus.publish_new(EVENT_LOG_ENTRY, {
                    "level": level,
                    "source": source,
                    "message": message,
                }, source="system")

            except Exception as e:
                print(f"[SimEngine] Log loop error: {e}")
                await asyncio.sleep(3)

    # ─── COMMAND INTERFACE ───────────────────────────────────────────────

    async def command_isolate(self, mac: str) -> dict:
        """User-triggered isolate command."""
        if mac not in self.devices:
            return {"success": False, "error": "Device not found"}

        device = self.devices[mac]
        fake_attack = {
            "id": f"MANUAL-{int(time.time())}",
            "name": "Manual Isolation",
            "severity": "high",
            "description": f"Manual isolation triggered for {device['hostname']}",
            "source_ip": "operator",
            "target_ip": device["ip"],
            "target_mac": mac,
            "type": "manual",
        }

        await self.agent_gamma.isolate_device(mac, device["ip"], "full_isolation", fake_attack, self.devices)

        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "CRITICAL",
            "source": "OPERATOR",
            "message": f"MANUAL_ISOLATE: Operator triggered isolation for {device['hostname']} ({mac})",
        }, source="operator")

        return {"success": True, "device": mac, "action": "isolated"}

    async def command_release(self, mac: str) -> dict:
        """User-triggered release command."""
        result = await self.agent_gamma.release_device(mac, self.devices)
        if result:
            return {"success": True, "device": mac, "action": "released"}
        return {"success": False, "error": "Device not found in isolation"}

    async def command_deploy_honeypot(self, target_ip: str, pot_type: str = "generic") -> dict:
        """User-triggered honeypot deployment."""
        pot_id = await self.agent_beta.deploy_honeypot(
            target_ip, pot_type, "operator_target", f"MANUAL-HP-{int(time.time())}"
        )

        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "INFO",
            "source": "OPERATOR",
            "message": f"MANUAL_HONEYPOT: Operator deployed {pot_type} honeypot on {target_ip}",
        }, source="operator")

        return {"success": True, "honeypot_id": pot_id, "target": target_ip, "type": pot_type}

    async def command_set_state(self, state: str) -> dict:
        """User-triggered system state change."""
        valid_states = [STATE_MONITORING, STATE_ALERT, STATE_DEFENSE, STATE_LOCKDOWN]
        if state not in valid_states:
            return {"success": False, "error": f"Invalid state. Valid: {valid_states}"}

        event_bus.set_system_state(state)

        await event_bus.publish_new(EVENT_LOG_ENTRY, {
            "level": "CRITICAL",
            "source": "OPERATOR",
            "message": f"STATE_OVERRIDE: System state changed to {state} by operator",
        }, source="operator")

        return {"success": True, "new_state": state}

    # ─── STATUS ──────────────────────────────────────────────────────────

    def get_full_status(self) -> dict:
        """Get complete system status for API."""
        return {
            "system_state": event_bus.system_state,
            "speed_mode": self.speed_mode,
            "uptime": int(time.time() - self.start_time) if self.start_time else 0,
            "cycles": self.cycle_count,
            "devices": {
                "total": len(self.devices),
                "online": len([d for d in self.devices.values() if d["status"] == "online"]),
                "isolated": len([d for d in self.devices.values() if d["status"] == "isolated"]),
                "suspicious": len([d for d in self.devices.values() if d["status"] == "suspicious"]),
            },
            "agents": {
                "alpha": self.agent_alpha.get_status(),
                "beta": self.agent_beta.get_status(),
                "gamma": self.agent_gamma.get_status(),
            },
            "threats": {
                "active": len(self.attack_simulator.get_active_attacks()),
                "total": len(self.attack_simulator.get_attack_history()),
            },
            "honeypots": {
                "active": len([h for h in self.agent_beta.honeypots.values() if h["status"] == "active"]),
                "total": self.agent_beta.honeypot_counter,
            },
            "event_bus": event_bus.get_stats(),
        }

    def get_all_devices(self) -> List[dict]:
        """Get all devices as a list."""
        return list(self.devices.values())

    def get_device(self, mac: str) -> Optional[dict]:
        """Get a single device by MAC."""
        return self.devices.get(mac)
