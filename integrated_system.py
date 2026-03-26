#!/usr/bin/env python3
"""
Integration between Agent Alpha (threat detection) and Agent Gamma (network filtering)
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.alpha.alpha import AgentAlpha
from agents.gamma.gamma import AgentGamma
from agents.gamma.segmentation import MicroSegmentation
from agents.gamma.adaptive import AdaptiveDefense
from agents.gamma.decision import DecisionEngine

class ThreatResponseSystem:
    def __init__(self):
        print("[+] Initializing Threat Response System...")

        # Initialize network interface
        self.interface = AgentAlpha.get_active_interface()
        print(f"[+] Using interface: {self.interface}")

        # Initialize Agent Alpha (threat detection)
        self.alpha = AgentAlpha(interface=self.interface)

        # Initialize Agent Gamma (network filtering)
        self.gamma = AgentGamma(interface=self.interface)
        self.segmentation = MicroSegmentation(self.gamma)
        self.adaptive = AdaptiveDefense(self.gamma)
        self.brain = DecisionEngine(self.gamma, self.segmentation, self.adaptive)

        # Connect Alpha's threat detection to Gamma's response system
        self.alpha.add_threat_callback(self.handle_threat)

        print("[+] Threat Response System initialized")
        print("[+] Alpha (detection) ↔ Gamma (response) connected")

    def handle_threat(self, threat):
        """Handle threats detected by Alpha using Gamma's response system."""
        print(f"\n[!!!] THREAT DETECTED: {threat['type']} - {threat['description']}")
        print(f"[!!!] Target: MAC {threat['mac']}, IP {threat.get('ip', 'unknown')}")
        print(f"[!!!] Severity: {threat['severity']}")

        # Convert Alpha's threat format to Gamma's expected format
        gamma_threat = self.convert_threat_format(threat)

        # Process threat through Gamma's decision engine
        try:
            self.brain.process_threat(gamma_threat)
            print(f"[+] Response executed for threat: {threat['type']}")
        except Exception as e:
            print(f"[ERROR] Failed to process threat: {e}")

    def convert_threat_format(self, alpha_threat):
        """Convert Alpha's threat format to Gamma's expected format."""
        threat_type = alpha_threat['type']
        mac = alpha_threat['mac']
        ip = alpha_threat.get('ip')

        if threat_type == "vm_detected":
            # VMs get micro-segmentation with limited services
            return {
                "type": "device_compromise",
                "mac": mac,
                "ip": ip,
                "allowed_services": ["8.8.8.8", "1.1.1.1"],  # DNS only
                "reason": "VM detected - restricting to essential services"
            }

        elif threat_type == "device_spoofing":
            # Device spoofing gets complete isolation
            return {
                "type": "device_compromise",
                "mac": mac,
                "ip": ip,
                "allowed_services": [],  # Complete isolation
                "reason": "Device spoofing detected - complete isolation"
            }

        elif threat_type == "suspicious_ports":
            # Suspicious ports get lateral movement blocking
            return {
                "type": "lateral",
                "mac": mac,
                "ip": ip,
                "lan_ips": ["192.168.1.0/24"],  # Block local network access
                "reason": "Suspicious port activity - blocking lateral movement"
            }

        elif threat_type == "high_traffic":
            # High traffic gets rate limiting through segmentation
            return {
                "type": "device_compromise",
                "mac": mac,
                "ip": ip,
                "allowed_services": ["8.8.8.8", "1.1.1.1", "208.67.222.222"],  # DNS only
                "reason": "High traffic detected - limiting to DNS"
            }

        elif threat_type == "ttl_anomaly":
            # TTL anomalies get monitoring but allow normal services
            return {
                "type": "device_compromise",
                "mac": mac,
                "ip": ip,
                "allowed_services": ["8.8.8.8", "1.1.1.1", "208.67.222.222", "1.0.0.1"],  # DNS
                "reason": "TTL anomaly detected - monitoring mode"
            }

        else:
            # Default response for unknown threats
            return {
                "type": "device_compromise",
                "mac": mac,
                "ip": ip,
                "allowed_services": ["8.8.8.8", "1.1.1.1"],  # Minimal access
                "reason": f"Unknown threat type: {threat_type}"
            }

    def start(self):
        """Start the integrated threat detection and response system."""
        print("THREAT RESPONSE SYSTEM ACTIVE")
        print("Alpha monitoring network traffic...")
        print("Gamma ready to respond to threats...")
        print("Detection -> Response pipeline active")

        try:
            # Start Alpha's packet capture (blocking)
            self.alpha.start()

        except KeyboardInterrupt:
            print("\nShutting down Threat Response System...")
            self.gamma.cleanup()
            self.alpha.save_devices()
            print("System shutdown complete")

    def get_status(self):
        """Get current system status."""
        return {
            "alpha_devices": len(self.alpha.devices),
            "gamma_blocked_ips": len(self.gamma.blocked_ips_map),
            "gamma_blocked_macs": len(self.gamma.blocked_macs_map),
            "threats_processed": self.alpha.threat_queue.qsize()
        }

def main():
    system = ThreatResponseSystem()
    system.start()

if __name__ == "__main__":
    main()