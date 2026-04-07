import logging

# Optional CVE database support
try:
    from intelligence.vector_db.cve_vector_db import CVEDatabase
    CVE_DB_AVAILABLE = True
except ImportError:
    CVE_DB_AVAILABLE = False
    CVEDatabase = None

logger = logging.getLogger('nemesis')

class RiskEngine:
    def __init__(self):
        if CVE_DB_AVAILABLE and CVEDatabase:
            try:
                self.cve_db = CVEDatabase()
                self._load_sample_cves()
            except Exception as e:
                logger.warning(f"CVE database initialization failed: {e}")
                self.cve_db = None
        else:
            logger.warning("CVE database not available (faiss module missing)")
            self.cve_db = None

    def _load_sample_cves(self):
        """Load sample CVEs for demonstration"""
        if not self.cve_db:
            return
            
        sample_cves = [
            "Linux SSH brute force vulnerability",
            "Windows RDP remote code execution",
            "IoT device default credentials",
            "Router buffer overflow vulnerability",
            "Smart device network access vulnerability",
        ]
        for cve_description in sample_cves:
            try:
                self.cve_db.add_cve(cve_description)
            except Exception as e:
                logger.debug(f"Failed to load sample CVE: {e}")

    def compute_risk(self, device):
        """Compute comprehensive risk score for device"""
        risk = 0
        
        # Factor 1: Device type baseline risk
        device_type = device.get('device_type', 'Unknown')
        if device_type == 'Router':
            risk += 15
        elif device_type == 'Windows':
            risk += 10
        elif device_type == 'Linux':
            risk += 5
        
        # Factor 2: Behavioral anomalies
        if device.get('vm_detected', False):
            risk += 25
        
        # Factor 3: Exposed ports
        ports = device.get('ports', set())
        if 22 in ports:
            risk += 20
        if 3389 in ports:
            risk += 20
        if 445 in ports:
            risk += 25
        
        # Factor 4: TTL anomalies
        if device.get('ttl_stability', 0) < 3:
            risk += 15
        
        # Factor 5: CVE correlation
        if self.cve_db:
            query = f"{device.get('device_type')} {device.get('fingerprint', 'generic')}"
            try:
                matches = self.cve_db.search(query)
                if matches:
                    risk += 30
            except Exception as e:
                logger.debug(f"CVE search failed: {e}")
        
        # Factor 6: Geographic indicators
        if device.get('country') in ['KP', 'IR', 'SY', 'RU', 'CN']:
            risk += 20
        
        # Factor 7: Packet anomalies
        packet_count = device.get('packet_count', 0)
        if packet_count > 5000:
            risk += 10
        elif packet_count < 5:
            risk += 5
        
        # Factor 8: Device type changes
        if device.get('device_type_history', []):
            if len(device.get('device_type_history', [])) > 2:
                risk += 30
        
        return min(max(risk, 0), 100)