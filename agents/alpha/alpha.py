#!/usr/bin/env python3
import scapy.all as scapy
import time
import json
import sys
from datetime import datetime
import os
from collections import defaultdict


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

class AgentAlpha:
    @staticmethod
    def get_active_interface():
        interfaces = scapy.get_if_list()
        for iface in interfaces:
            if iface != "lo":
                return iface
        return "eth0"

    def __init__(self, interface='wlan0'):
        self.interface = interface
        self.devices = {}
        self.running = True
        self.ttl_history = defaultdict(list)  # Track TTL values over time
        self.mac_to_device_type = {}  # Track device type changes

        # Ensure directories exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)

    def packet_handler(self, packet):
        try:
            now = datetime.now().isoformat()

            #ARP handling
            if scapy.ARP in packet:
                mac = packet.hwsrc
                ip = packet.psrc
                self.update_device(mac, ip, None, None, now)
                return

            # IP packet handling
            if not packet.haslayer(scapy.IP):
                return

            src_mac = packet.src
            src_ip = packet[scapy.IP].src
            ttl = packet[scapy.IP].ttl

            tcp_win = None
            dst_port = None

            if packet.haslayer(scapy.TCP):
                tcp_win = packet[scapy.TCP].window
                dst_port = packet[scapy.TCP].dport

            # Update device info
            self.update_device(src_mac, src_ip, ttl, tcp_win, now, dst_port)

            # Log packet
            self.log_packet(src_mac, src_ip, ttl, tcp_win)

        except Exception as e:
            print(f"[ERROR] Packet processing failed: {e}")

    def update_device(self, mac, ip, ttl, tcp_win, now, port=None):
        if mac not in self.devices:
            self.devices[mac] = {
                'first_seen': now,
                'last_seen': now,
                'ip': ip,
                'ttl': ttl,
                'tcp_window': tcp_win,
                'fingerprint': self.fingerprint(ttl, tcp_win),
                'packet_count': 1,
                'ports': set(),
                'ttl_stability': 0,
                'vm_detected': self.is_vm_device(mac),
                'device_type_history': []
            }
            if ttl:
                self.ttl_history[mac].append({'ttl': ttl, 'time': now})
        else:
            device = self.devices[mac]
            device['last_seen'] = now
            device['ip'] = ip
            device['packet_count'] += 1

            # Track TTL changes more accurately
            if ttl is not None:
                self.ttl_history[mac].append({'ttl': ttl, 'time': now})
                
                # Detect significant TTL change (VM to real machine or vice versa)
                current_type = self.identify_device_type(ttl)
                previous_type = self.identify_device_type(device['ttl']) if device['ttl'] else None
                
                if previous_type and current_type and current_type != previous_type:
                    change_info = {
                        'from': previous_type,
                        'to': current_type,
                        'time': now,
                        'old_ttl': device['ttl'],
                        'new_ttl': ttl
                    }
                    print(f"[!] DEVICE TYPE CHANGE for {mac}: {previous_type} ({device['ttl']}) -> {current_type} ({ttl})")
                    device['device_type_history'].append(change_info)
                    device['vm_detected'] = self.is_vm_device(mac)
                    self.log_anomaly(mac, "device_type_change", change_info)
                
                # Update TTL with stability check
                if device['ttl'] != ttl:
                    device['ttl'] = ttl
                    device['fingerprint'] = self.fingerprint(ttl, tcp_win)
                    device['ttl_stability'] = 0
                else:
                    device['ttl_stability'] += 1

        if port:
            self.devices[mac]['ports'].add(port)

    def fingerprint(self, ttl, tcp_win):
        """Enhanced fingerprinting with better accuracy"""
        if ttl is None:
            return "Unknown"

        device_type = self.identify_device_type(ttl)
        
        # Enhanced fingerprinting based on TCP window
        if device_type == "Linux":
            if tcp_win == 5840:
                return "Linux (Kernel 2.6.x)"
            elif tcp_win == 29200:
                return "Linux (Kernel 3.x/4.x)"
            elif tcp_win == 65535:
                return "Linux (Kernel 5.x+)"
            elif tcp_win in [8192, 16384, 32768]:
                return "Linux (Custom Kernel)"
            return "Linux (Generic)"

        elif device_type == "Windows":
            if tcp_win == 8192:
                return "Windows XP/2003"
            elif tcp_win == 16384:
                return "Windows Vista/7"
            elif tcp_win == 65535:
                return "Windows 8/10/11"
            elif tcp_win == 32768:
                return "Windows Server"
            return "Windows (Generic)"

        elif device_type == "macOS":
            return "macOS/iOS"
        elif device_type == "Router":
            return "Network Device / Router"
        
        return "Unknown"

    def identify_device_type(self, ttl):
        """Identify device OS type from TTL value"""
        if ttl is None:
            return None
        
        if ttl >= 64 and ttl <= 76:
            return "Linux"
        elif ttl >= 100 and ttl <= 128:
            return "Windows"
        elif ttl >= 200 and ttl <= 255:
            return "Router"
        elif ttl >= 60 and ttl <= 64:
            return "macOS"
        
        return "Unknown"

    def is_vm_device(self, mac):
        """Detect if device is running in a VM based on MAC address"""
        mac_upper = mac.upper()
        
        # Common VM MAC address prefixes
        vm_prefixes = [
            "08:00:27",  # VirtualBox
            "00:0C:29",  # VMware
            "00:1C:42",  # Parallels
            "54:52:00",  # QEMU
            "52:54:00",  # QEMU/KVM
            "06:FE:00",  # Hyper-V
        ]
        
        for prefix in vm_prefixes:
            if mac_upper.startswith(prefix):
                return True
        
        return False

    def detect_ttl_anomaly(self, mac):
        """Detect anomalies in TTL history for a device"""
        if mac not in self.ttl_history or len(self.ttl_history[mac]) < 3:
            return None
        
        ttl_values = [entry['ttl'] for entry in self.ttl_history[mac][-10:]]
        
        if len(set(ttl_values)) > 1:
            # Multiple different TTL values detected
            transitions = []
            for i in range(1, len(ttl_values)):
                if ttl_values[i] != ttl_values[i-1]:
                    transitions.append({
                        'from': ttl_values[i-1],
                        'to': ttl_values[i]
                    })
            return transitions if transitions else None
        
        return None

    def log_packet(self, mac, ip, ttl, win):
        log = {
            "time": time.time(),
            "mac": mac,
            "ip": ip,
            "ttl": ttl,
            "window": win,
            "device_type": self.identify_device_type(ttl)
        }

        with open(os.path.join(LOG_DIR, 'packets.log'), 'a') as f:
            f.write(json.dumps(log) + "\n")

    def log_anomaly(self, mac, anomaly_type, details):
        """Log detected anomalies like TTL changes"""
        log = {
            "time": datetime.now().isoformat(),
            "mac": mac,
            "anomaly_type": anomaly_type,
            "details": details
        }

        with open(os.path.join(LOG_DIR, 'anomalies.log'), 'a') as f:
            f.write(json.dumps(log) + "\n")

    def save_devices(self):
        # Convert sets to lists for JSON
        serializable_data = {}

        for mac, data in self.devices.items():
            serializable_data[mac] = data.copy()
            serializable_data[mac]['ports'] = list(data['ports'])
            
            # Add TTL history and anomaly detection
            if mac in self.ttl_history:
                serializable_data[mac]['ttl_history'] = self.ttl_history[mac]
                serializable_data[mac]['ttl_anomalies'] = self.detect_ttl_anomaly(mac)

        with open(os.path.join(DATA_DIR, 'devices.json'), 'w') as f:
            json.dump(serializable_data, f, indent=2)

    def start(self):
        print(f"[+] Starting capture on {self.interface}")

        scapy.sniff(
            iface=self.interface,
            prn=self.packet_handler,
            store=0,
            filter="arp or ip"
        )

if __name__ == "__main__":
    
    alpha = AgentAlpha(interface=AgentAlpha.get_active_interface())

    try:
        alpha.start()

    except KeyboardInterrupt:
        print("\n[+] Stopping capture...")
        alpha.save_devices()
        print("[+] Devices saved to data/devices.json")
        sys.exit(0)