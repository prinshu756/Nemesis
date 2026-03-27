from intelligence.vector_db.cve_vector_db import CVEDatabase

class RiskEngine:
    def __init__(self):
        self.cve_db = CVEDatabase()

    def compute_risk(self, device):
        risk = device.get("risk_score", 0)

        query = f"{device.get('device_type')} {device.get('traffic_pattern')}"
        matches = self.cve_db.search(query)

        if matches:
            risk += 30

        if device.get("country") == "RU":
            risk += 20

        return min(risk, 100)