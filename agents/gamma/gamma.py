import socket, struct, subprocess, os

class AgentGamma:
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.blocked_ips_map = {}
        self.blocked_macs_map = {}
        self.ebpf_attached = False

        # Compile if needed
        self._ensure_compiled()
        
        # Try to load eBPF 
        self._try_load_ebpf()

        print("[+] Gamma Loaded with MAC filtering")

    def _ensure_compiled(self):
        """Ensure gamma_ebpf.o exists."""
        if not os.path.exists("gamma_ebpf.o"):
            print("[*] Compiling gamma_ebpf.c...")
            try:
                subprocess.run([
                    "clang", "-O2", "-target", "bpf",
                    "-I/usr/include", "-I/usr/include/bpf",
                    "-c", "gamma_ebpf.c", "-o", "gamma_ebpf.o"
                ], check=True, capture_output=True)
                print("[+] Compiled gamma_ebpf.o")
            except Exception as e:
                print(f"[!] Compile failed: {e}")

    def _try_load_ebpf(self):
        """Try to load eBPF program. If fails, continue with local tracking."""
        try:
            if not os.path.exists("gamma_ebpf.o"):
                # Silently use local tracking if object doesn't exist
                return
            
            # Try to attach with ip command
            result = subprocess.run([
                "ip", "link", "set", "dev", self.interface,
                "xdp", "obj", "gamma_ebpf.o", "section", "xdp"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.ebpf_attached = True
                print(f"[+] XDP loaded on {self.interface}")
            # Silently continue with local tracking on failure
        except Exception as e:
            # Silently continue with local tracking
            pass

    def ip_to_int(self, ip):
        return struct.unpack("!I", socket.inet_aton(ip))[0]

    def mac_to_bytes(self, mac):
        return bytes.fromhex(mac.replace(":", ""))

    # IP Control
    def block_ip(self, ip):
        self.blocked_ips_map[self.ip_to_int(ip)] = 1
        print(f"[+] Blocked IP: {ip}")

    # MAC Control 
    def block_mac(self, mac):
        mac_bytes = self.mac_to_bytes(mac)
        self.blocked_macs_map[mac_bytes] = 1
        print(f"[+] Blocked MAC: {mac}")

    def unblock_mac(self, mac):
        mac_bytes = self.mac_to_bytes(mac)
        try:
            del self.blocked_macs_map[mac_bytes]
        except KeyError:
            pass

    def unblock_ip(self, ip):
        """Unblock an IP address."""
        ip_int = self.ip_to_int(ip)
        try:
            del self.blocked_ips_map[ip_int]
        except KeyError:
            pass
        print(f"[+] Unblocked IP: {ip}")

    def allow_ip_for_mac(self, mac, ip):
        """Whitelist specific IP for a MAC address."""
        print(f"[+] Allowing {ip} for MAC {mac}")
        # Track allowed services per MAC
        if not hasattr(self, 'allowed_services_map'):
            self.allowed_services_map = {}
        mac_bytes = self.mac_to_bytes(mac)
        if mac_bytes not in self.allowed_services_map:
            self.allowed_services_map[mac_bytes] = set()
        self.allowed_services_map[mac_bytes].add(self.ip_to_int(ip))

    def block_ip_for_mac(self, mac, ip):
        """Block specific IP for a MAC address (lateral movement prevention)."""
        print(f"[+] Blocking {ip} for MAC {mac}")
        if not hasattr(self, 'blocked_services_map'):
            self.blocked_services_map = {}
        mac_bytes = self.mac_to_bytes(mac)
        if mac_bytes not in self.blocked_services_map:
            self.blocked_services_map[mac_bytes] = set()
        self.blocked_services_map[mac_bytes].add(self.ip_to_int(ip))

    def cleanup(self):
        if self.ebpf_attached:
            try:
                subprocess.run([
                    "ip", "link", "set", "dev", self.interface, "xdp", "off"
                ], check=True, capture_output=True, timeout=5)
                print("[+] XDP Detached")
            except Exception as e:
                print(f"[!] Cleanup failed: {e}")
        else:
            print("[+] No XDP to detach (local tracking only)")