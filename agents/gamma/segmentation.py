class MicroSegmentation:
    def __init__(self, gamma):
        self.gamma = gamma  

    def isolate_device(self, mac):
        #Block everything from device
        self.gamma.isolate_device(mac)

    def allow_services(self, mac, allowed_ips):
        #Allow only specific services (e.g., Netflix
        for ip in allowed_ips:
            self.gamma.allow_ip_for_mac(mac, ip)

        # Drop all other traffic
        self.gamma.block_mac(mac)

    def block_lateral_movement(self, mac, local_network_range):
        #Prevent access to LAN devices
        for network in local_network_range:
            if '/' in network:
                # Handle CIDR notation - block representative IPs from the range
                base_ip = network.split('/')[0]
                # Block the network base and a few key IPs
                self.gamma.block_ip_for_mac(mac, base_ip)
                # For demo purposes, block .1, .254 (gateway, broadcast)
                parts = base_ip.split('.')
                if len(parts) == 4:
                    gateway = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                    broadcast = f"{parts[0]}.{parts[1]}.{parts[2]}.254"
                    self.gamma.block_ip_for_mac(mac, gateway)
                    self.gamma.block_ip_for_mac(mac, broadcast)
                print(f"[+] Blocked lateral movement for {mac} in network {network}")
            else:
                # Handle individual IP
                self.gamma.block_ip_for_mac(mac, network)