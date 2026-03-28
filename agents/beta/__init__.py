class AgentBeta:
    def __init__(self):
        self.active_honeypots = {}
    
    def deploy_honeypot(self, ip, threat_type='generic'):
        """Deploy a honeypot for an IP address"""
        print(f"Deploying honeypot for IP: {ip} ({threat_type})")
        container_id = f"honeypot_{ip.replace('.', '_')}"
        self.active_honeypots[ip] = {
            'container_id': container_id,
            'threat_type': threat_type,
            'active': True
        }
        return container_id
    
    def get_active_honeypots(self):
        """Get list of active honeypots"""
        return [ip for ip, hp in self.active_honeypots.items() if hp.get('active', False)]
    
    def cleanup_honeypot(self, ip):
        """Clean up honeypot for an IP"""
        if ip in self.active_honeypots:
            self.active_honeypots[ip]['active'] = False
            print(f"Cleaned up honeypot for {ip}")
            return True
        return False