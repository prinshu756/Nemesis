import yaml
import os

class Config:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self.get_default_config()

    def get_default_config(self):
        return {
            'network': {
                'interface': 'eth0',
                'monitor_mode': True
            },
            'ai': {
                'model': 'all-MiniLM-L6-v2',
                'ollama_url': 'http://localhost:11434',
                'use_local_ai': False
            },
            'risk_thresholds': {
                'high': 80,
                'medium': 50,
                'low': 20
            },
            'honeypot': {
                'enabled': True,
                'images': ['cowrie/cowrie:latest', 'dionaea:latest'],
                'auto_deploy': True
            },
            'ebpf': {
                'enabled': True,
                'auto_compile': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/nemesis.log',
                'max_size': 10485760,  # 10MB
                'backup_count': 5
            }
        }

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

config = Config()