class StateManager:
    def __init__(self):
        self.devices = {}
        self.alerts = []

    def update_device(self, mac, device):
        self.devices[mac] = device

    def add_alert(self, alert):
        self.alerts.append(alert)
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]