class DecisionEngine:
    def __init__(self, gamma, segmentation, adaptive):
        self.gamma = gamma
        self.segmentation = segmentation
        self.adaptive = adaptive

    def process_threat(self, threat):
        """
        threat = {
            "type": "C2" | "lateral" | "device_compromise",
            "ip": "...",
            "mac": "...",
            "allowed_services": []
        }
        """

        if threat["type"] == "C2":
            print("[*] Blocking Command & Control server")
            self.gamma.block_ip(threat["ip"])

        elif threat["type"] == "lateral":
            print("[*] Blocking lateral movement")
            self.segmentation.block_lateral_movement(
                threat["mac"],
                threat.get("lan_ips", [])
            )

        elif threat["type"] == "device_compromise":
            print("[*] Applying micro-segmentation")

            self.segmentation.allow_services(
                threat["mac"],
                threat["allowed_services"]
            )