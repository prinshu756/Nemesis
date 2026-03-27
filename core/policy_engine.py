class PolicyEngine:
    def decide(self, risk_score):
        if risk_score > 80:
            return "isolate"
        elif risk_score > 50:
            return "honeypot"
        else:
            return "monitor"