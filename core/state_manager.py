"""
State Management for Nemesis SOC
Maintains current device and alert state
"""

from typing import Dict, List, Any
from datetime import datetime


class StateManager:
    """Manages the current state of devices and alerts"""
    
    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.vulnerabilities: Dict[str, List] = {}
        self.policies: Dict[str, Any] = {}
    
    def update_device(self, mac: str, device_info: Dict[str, Any]):
        """Update device information in state"""
        if mac not in self.devices:
            self.devices[mac] = {}
        
        self.devices[mac].update(device_info)
        self.devices[mac]['last_updated'] = datetime.utcnow().isoformat()
    
    def get_device(self, mac: str) -> Dict[str, Any]:
        """Get device information from state"""
        return self.devices.get(mac, {})
    
    def add_alert(self, alert: Dict[str, Any]):
        """Add an alert to state"""
        alert['timestamp'] = datetime.utcnow().isoformat()
        self.alerts.append(alert)
        
        # Keep only latest 100 alerts in memory
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts[-limit:]
    
    def update_vulnerability(self, device_mac: str, vuln_info: Dict[str, Any]):
        """Update vulnerability information for a device"""
        if device_mac not in self.vulnerabilities:
            self.vulnerabilities[device_mac] = []
        
        self.vulnerabilities[device_mac].append(vuln_info)
    
    def get_vulnerabilities(self, device_mac: str) -> List[Dict[str, Any]]:
        """Get vulnerabilities for a device"""
        return self.vulnerabilities.get(device_mac, [])
    
    def update_policy(self, policy_name: str, policy_config: Dict[str, Any]):
        """Update policy information"""
        self.policies[policy_name] = policy_config
    
    def get_policy(self, policy_name: str) -> Dict[str, Any]:
        """Get policy information"""
        return self.policies.get(policy_name, {})
    
    def clear_old_data(self, max_devices: int = 1000):
        """Clear old data if exceeds limits"""
        if len(self.devices) > max_devices:
            # Remove devices not seen in last hour
            devices_to_remove = []
            for mac, device in self.devices.items():
                # In a real implementation, check last_seen timestamp
                pass
            
            for mac in devices_to_remove:
                del self.devices[mac]
