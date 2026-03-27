from intelligence.vector_db.cve_vector_db import CVEDatabase
from core.logging_config import logger
from core.config import config
import requests
import json
from datetime import datetime

class RiskEngine:
    def __init__(self):
        self.cve_db = CVEDatabase()
        self.use_local_ai = config.get('ai.use_local_ai', False)
        self.ollama_url = config.get('ai.ollama_url', 'http://localhost:11434')
        self.model = config.get('ai.model', 'all-MiniLM-L6-v2')
        logger.info("Risk Engine initialized with AI integration")

    def compute_risk(self, device):
        """Enhanced risk computation with AI analysis"""
        try:
            base_risk = device.get("risk_score", 0)

            # CVE-based risk
            cve_risk = self._assess_cve_risk(device)
            base_risk += cve_risk

            # Behavioral risk
            behavioral_risk = self._assess_behavioral_risk(device)
            base_risk += behavioral_risk

            # AI-powered contextual analysis
            if self.use_local_ai:
                ai_risk = self._ai_contextual_analysis(device)
                base_risk += ai_risk

            # Geographic risk
            geo_risk = self._assess_geographic_risk(device)
            base_risk += geo_risk

            final_risk = min(max(base_risk, 0), 100)

            logger.info(f"Risk assessment for {device.get('mac')}: {final_risk}")
            return final_risk

        except Exception as e:
            logger.error(f"Risk computation failed: {e}")
            return 50  # Default medium risk

    def _assess_cve_risk(self, device):
        """Assess risk based on CVE matches"""
        try:
            device_type = device.get('device_type', 'Unknown')
            fingerprint = device.get('fingerprint', '')

            query = f"{device_type} {fingerprint} {device.get('traffic_pattern', '')}"
            matches = self.cve_db.search(query)

            if matches:
                # Weight by severity and recency
                risk = min(len(matches) * 15, 40)
                logger.debug(f"CVE matches for {device.get('mac')}: {len(matches)} matches, risk: {risk}")
                return risk
            return 0
        except Exception as e:
            logger.error(f"CVE assessment failed: {e}")
            return 10

    def _assess_behavioral_risk(self, device):
        """Assess risk based on device behavior"""
        risk = 0

        # High packet count
        packet_count = device.get('packet_count', 0)
        if packet_count > 10000:
            risk += 20
        elif packet_count > 1000:
            risk += 10

        # Suspicious ports
        ports = device.get('ports', set())
        suspicious_ports = {22, 23, 3389, 5900, 4444, 6667, 31337}
        suspicious_found = len(ports.intersection(suspicious_ports))
        risk += suspicious_found * 5

        # TTL anomalies
        ttl_anomalies = device.get('ttl_anomalies', [])
        risk += len(ttl_anomalies) * 3

        # Device type changes
        type_history = device.get('device_type_history', [])
        risk += len(type_history) * 8

        return min(risk, 30)

    def _assess_geographic_risk(self, device):
        """Assess risk based on geographic indicators"""
        risk = 0

        # Known high-risk countries
        high_risk_countries = {'RU', 'CN', 'IR', 'KP', 'CU'}
        country = device.get('country', '').upper()

        if country in high_risk_countries:
            risk += 20
        elif country:
            risk += 5  # Unknown countries get slight penalty

        return risk

    def _ai_contextual_analysis(self, device):
        """Use AI for contextual risk analysis"""
        try:
            if not self._check_ollama_available():
                return 0

            prompt = self._build_ai_prompt(device)

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                risk_score = self._parse_ai_response(result.get('response', ''))
                logger.debug(f"AI analysis for {device.get('mac')}: {risk_score}")
                return risk_score
            else:
                logger.warning(f"AI analysis failed: {response.status_code}")
                return 0

        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return 0

    def _check_ollama_available(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _build_ai_prompt(self, device):
        """Build prompt for AI analysis"""
        return f"""Analyze this network device for security risk. Provide a risk score from 0-30 based on context.

Device Info:
- MAC: {device.get('mac')}
- IP: {device.get('ip')}
- Device Type: {device.get('device_type')}
- Fingerprint: {device.get('fingerprint')}
- Packet Count: {device.get('packet_count', 0)}
- Ports Used: {list(device.get('ports', set()))}
- TTL History: {len(device.get('ttl_history', []))} changes
- VM Detected: {device.get('vm_detected', False)}
- Country: {device.get('country', 'Unknown')}

Consider:
- Unusual behavior patterns
- Potential attack indicators
- Device type consistency
- Network positioning

Return only a number from 0-30 representing additional risk:"""

    def _parse_ai_response(self, response):
        """Parse AI response to extract risk score"""
        try:
            # Extract first number found
            import re
            numbers = re.findall(r'\d+', response.strip())
            if numbers:
                score = int(numbers[0])
                return max(0, min(score, 30))
        except:
            pass
        return 0