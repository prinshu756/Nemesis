class AdaptiveDefense:
    def __init__(self, gamma):
        self.gamma = gamma
        self.mac_ip_history = {}

    def track_activity(self, mac, ip):
        """Track which IPs a MAC communicates with"""
        if mac not in self.mac_ip_history:
            self.mac_ip_history[mac] = set()

        self.mac_ip_history[mac].add(ip)

    def detect_anomaly(self, mac, ip):
        """Simple anomaly detection"""
        known_ips = self.mac_ip_history.get(mac, set())

        if ip not in known_ips:
            print(f"[!] New suspicious IP {ip} for {mac}")
            return True
        return False

    def auto_block(self, mac, ip):
        """Automatically block new malicious IP"""
        if self.detect_anomaly(mac, ip):
            self.gamma.block_ip(ip)
            print(f"[+] Adaptive block applied: {ip}")