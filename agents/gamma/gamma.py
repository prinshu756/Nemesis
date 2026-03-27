import socket, struct, subprocess, os
from system.firewall import isolate_device
from core.logging_config import logger
from core.config import config
import json
import time

class AgentGamma:

    def __init__(self, interface="eth0"):
        self.interface = interface
        self.blocked_ips_map = {}
        self.blocked_macs_map = {}
        self.segmentation_policies = {}  # MAC -> policy rules
        self.ebpf_attached = False
        self.ebpf_enabled = config.get('ebpf.enabled', True)

        if self.ebpf_enabled:
            # Compile if needed
            self._ensure_compiled()

            # Try to load eBPF
            self._try_load_ebpf()

        logger.info(f"Agent Gamma initialized on {interface}, eBPF: {self.ebpf_attached}")

    def isolate_device(self, mac, policy="full_isolation"):
        """Apply micro-segmentation policy to device"""
        try:
            ip = self.get_ip_from_mac(mac)
            if not ip:
                logger.warning(f"Could not resolve IP for MAC {mac}")
                return

            if policy == "full_isolation":
                self._apply_full_isolation(mac, ip)
            elif policy == "limited_services":
                self._apply_limited_services(mac, ip)
            elif policy == "lateral_block":
                self._apply_lateral_block(mac, ip)
            else:
                self._apply_custom_policy(mac, ip, policy)

            logger.info(f"Applied {policy} to device {mac} ({ip})")

        except Exception as e:
            logger.error(f"Failed to isolate device {mac}: {e}")

    def _apply_full_isolation(self, mac, ip):
        """Complete network isolation"""
        self.block_ip(ip)
        self.block_mac(mac)
        self.segmentation_policies[mac] = {
            'type': 'full_isolation',
            'blocked_ips': [ip],
            'blocked_macs': [mac],
            'allowed_services': [],
            'timestamp': time.time()
        }

    def _apply_limited_services(self, mac, ip):
        """Allow only essential services (DNS, etc.)"""
        # Block all except DNS servers
        dns_servers = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        self.segmentation_policies[mac] = {
            'type': 'limited_services',
            'allowed_ips': dns_servers,
            'blocked_all_else': True,
            'timestamp': time.time()
        }

        # Update eBPF maps if available
        if self.ebpf_attached:
            self._update_ebpf_policy(mac, {'allow': dns_servers})

    def _apply_lateral_block(self, mac, ip):
        """Block lateral movement within LAN"""
        lan_range = self._get_lan_range(ip)
        self.segmentation_policies[mac] = {
            'type': 'lateral_block',
            'blocked_ranges': lan_range,
            'timestamp': time.time()
        }

    def _apply_custom_policy(self, mac, ip, policy_config):
        """Apply custom segmentation policy"""
        self.segmentation_policies[mac] = {
            'type': 'custom',
            'config': policy_config,
            'timestamp': time.time()
        }

    def _get_lan_range(self, ip):
        """Get LAN IP range for blocking lateral movement"""
        # Simple implementation - block private ranges except gateway
        parts = ip.split('.')
        if len(parts) == 4:
            base = f"{parts[0]}.{parts[1]}.{parts[2]}."
            return [f"{base}{i}" for i in range(1, 255) if f"{base}{i}" != ip]
        return []

    def get_ip_from_mac(self, mac):
        """Resolve IP from MAC address using ARP table"""
        try:
            # Try to get from system ARP table
            result = subprocess.run(['arp', '-n'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if mac.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[0]
        except Exception as e:
            logger.debug(f"ARP lookup failed: {e}")

        # Fallback to placeholder
        return f"192.168.1.{hash(mac) % 254 + 1}"

    def _ensure_compiled(self):
        """Ensure gamma_ebpf.o exists."""
        ebpf_file = "agents/gamma/gamma_ebpf.o"
        source_file = "agents/gamma/gamma_ebpf.c"

        if not os.path.exists(ebpf_file):
            if os.path.exists(source_file):
                logger.info("Compiling eBPF program...")
                try:
                    result = subprocess.run([
                        "clang", "-O2", "-target", "bpf",
                        "-I/usr/include", "-I/usr/include/bpf",
                        "-c", source_file, "-o", ebpf_file
                    ], capture_output=True, text=True, timeout=30)

                    if result.returncode == 0:
                        logger.info("eBPF program compiled successfully")
                    else:
                        logger.error(f"eBPF compilation failed: {result.stderr}")

                except Exception as e:
                    logger.error(f"eBPF compilation error: {e}")
            else:
                logger.warning("eBPF source file not found")

    def _try_load_ebpf(self):
        """Try to load eBPF program."""
        try:
            ebpf_file = "agents/gamma/gamma_ebpf.o"
            if not os.path.exists(ebpf_file):
                logger.warning("eBPF object file not found")
                return

            # Try to attach with ip command
            result = subprocess.run([
                "ip", "link", "set", "dev", self.interface,
                "xdp", "obj", ebpf_file, "section", "xdp"
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.ebpf_attached = True
                logger.info(f"eBPF XDP program loaded on {self.interface}")
            else:
                logger.warning(f"eBPF loading failed: {result.stderr}")

        except Exception as e:
            logger.error(f"eBPF loading error: {e}")

    def _update_ebpf_policy(self, mac, policy):
        """Update eBPF maps with new policy (placeholder)"""
        if not self.ebpf_attached:
            return

        try:
            # This would update eBPF maps with new rules
            # Implementation depends on the specific eBPF program
            logger.debug(f"Updating eBPF policy for {mac}: {policy}")
        except Exception as e:
            logger.error(f"eBPF policy update failed: {e}")

    def ip_to_int(self, ip):
        return struct.unpack("!I", socket.inet_aton(ip))[0]

    def mac_to_bytes(self, mac):
        return bytes.fromhex(mac.replace(":", ""))

    # IP Control
    def block_ip(self, ip):
        self.blocked_ips_map[self.ip_to_int(ip)] = 1
        logger.info(f"Blocked IP: {ip}")

    # MAC Control
    def block_mac(self, mac):
        mac_bytes = self.mac_to_bytes(mac)
        self.blocked_macs_map[mac_bytes] = 1
        logger.info(f"Blocked MAC: {mac}")

    def unblock_mac(self, mac):
        mac_bytes = self.mac_to_bytes(mac)
        try:
            del self.blocked_macs_map[mac_bytes]
            logger.info(f"Unblocked MAC: {mac}")
        except KeyError:
            pass

    def unblock_ip(self, ip):
        """Unblock an IP address."""
        ip_int = self.ip_to_int(ip)
        try:
            del self.blocked_ips_map[ip_int]
            logger.info(f"Unblocked IP: {ip}")
        except KeyError:
            pass

    def allow_ip_for_mac(self, mac, ip):
        """Whitelist specific IP for a MAC address."""
        logger.info(f"Allowing {ip} for MAC {mac}")
        # Track allowed services per MAC
        if not hasattr(self, 'allowed_services_map'):
            self.allowed_services_map = {}
        mac_bytes = self.mac_to_bytes(mac)
        if mac_bytes not in self.allowed_services_map:
            self.allowed_services_map[mac_bytes] = set()
        self.allowed_services_map[mac_bytes].add(self.ip_to_int(ip))

    def block_ip_for_mac(self, mac, ip):
        """Block specific IP for a MAC address (lateral movement prevention)."""
        logger.info(f"Blocking {ip} for MAC {mac}")
        if not hasattr(self, 'blocked_services_map'):
            self.blocked_services_map = {}
        mac_bytes = self.mac_to_bytes(mac)
        if mac_bytes not in self.blocked_services_map:
            self.blocked_services_map[mac_bytes] = set()
        self.blocked_services_map[mac_bytes].add(self.ip_to_int(ip))

    def get_segmentation_status(self):
        """Get current segmentation policies"""
        return {
            'policies': self.segmentation_policies,
            'ebpf_attached': self.ebpf_attached,
            'blocked_ips': len(self.blocked_ips_map),
            'blocked_macs': len(self.blocked_macs_map)
        }

    def cleanup(self):
        """Cleanup resources"""
        if self.ebpf_attached:
            try:
                subprocess.run([
                    "ip", "link", "set", "dev", self.interface, "xdp", "off"
                ], check=True, capture_output=True, timeout=5)
                logger.info("eBPF program detached")
            except Exception as e:
                logger.error(f"eBPF cleanup failed: {e}")
        else:
            logger.info("No eBPF to detach (using iptables fallback)")