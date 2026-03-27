import docker
import random
import string
from core.logging_config import logger
from core.config import config
import time
import threading

class AgentBeta:
    def __init__(self):
        self.client = None
        self.containers = {}
        self.honeypot_images = config.get('honeypot.images', ['cowrie/cowrie:latest'])
        self.auto_deploy = config.get('honeypot.auto_deploy', True)
        self._init_docker()
        logger.info("Agent Beta initialized with honeypot capabilities")

    def _init_docker(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            # Test the connection with a short timeout
            self.client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"Docker not available: {e}. Honeypot functionality will be simulated.")
            self.client = None

    def deploy_honeypot(self, target_ip, threat_type="generic"):
        """Deploy a honeypot for the given IP and threat type"""
        if not self.client or not self.auto_deploy:
            logger.warning("Docker not available or auto-deploy disabled")
            return None

        try:
            # Select appropriate honeypot image
            image = self._select_honeypot_image(threat_type)

            # Generate unique container name
            container_name = f"nemesis_honeypot_{target_ip.replace('.', '_')}_{int(time.time())}"

            # Configure container
            container_config = self._get_container_config(image, target_ip, threat_type)

            # Create and start container
            container = self.client.containers.run(
                image,
                name=container_name,
                detach=True,
                **container_config
            )

            # Store container info
            self.containers[target_ip] = {
                'container': container,
                'threat_type': threat_type,
                'created_at': time.time(),
                'image': image
            }

            logger.info(f"Deployed honeypot {container_name} for {target_ip} (threat: {threat_type})")

            # Start monitoring thread
            threading.Thread(target=self._monitor_container, args=(container, target_ip), daemon=True).start()

            return container_name

        except Exception as e:
            logger.error(f"Failed to deploy honeypot for {target_ip}: {e}")
            return None

    def _select_honeypot_image(self, threat_type):
        """Select appropriate honeypot image based on threat type"""
        image_map = {
            'ssh': 'cowrie/cowrie:latest',
            'web': 'dionaea:latest',
            'ftp': 'pyhoney:latest',
            'telnet': 'cowrie/cowrie:latest'
        }

        return image_map.get(threat_type, random.choice(self.honeypot_images))

    def _get_container_config(self, image, target_ip, threat_type):
        """Get container configuration for honeypot"""
        base_config = {
            'ports': {},
            'environment': {
                'HONEYPOT_TYPE': threat_type,
                'TARGET_IP': target_ip
            },
            'network_mode': 'bridge',
            'restart_policy': {'Name': 'unless-stopped'}
        }

        # Configure ports based on threat type
        if threat_type == 'ssh':
            base_config['ports']['2222/tcp'] = None  # Map to random host port
        elif threat_type == 'web':
            base_config['ports']['80/tcp'] = None
            base_config['ports']['443/tcp'] = None
        elif threat_type == 'ftp':
            base_config['ports']['21/tcp'] = None
        elif threat_type == 'telnet':
            base_config['ports']['23/tcp'] = None

        return base_config

    def _monitor_container(self, container, target_ip):
        """Monitor honeypot container for activity"""
        try:
            while True:
                container.reload()
                status = container.status

                if status != 'running':
                    logger.warning(f"Honeypot for {target_ip} stopped: {status}")
                    break

                # Check logs for activity (simplified)
                try:
                    logs = container.logs(tail=10).decode('utf-8')
                    if logs and len(logs.strip()) > 0:
                        logger.info(f"Honeypot activity detected for {target_ip}: {logs[-200:]}")
                except:
                    pass

                time.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"Container monitoring failed for {target_ip}: {e}")

    def cleanup_honeypot(self, target_ip):
        """Clean up honeypot for target IP"""
        if target_ip in self.containers:
            try:
                container_info = self.containers[target_ip]
                container_info['container'].stop()
                container_info['container'].remove()
                del self.containers[target_ip]
                logger.info(f"Cleaned up honeypot for {target_ip}")
            except Exception as e:
                logger.error(f"Failed to cleanup honeypot for {target_ip}: {e}")

    def get_active_honeypots(self):
        """Get list of active honeypots"""
        return {
            ip: {
                'threat_type': info['threat_type'],
                'image': info['image'],
                'uptime': time.time() - info['created_at']
            }
            for ip, info in self.containers.items()
        }

    def simulate_attack(self, target_ip, attack_type="ssh_brute_force"):
        """Simulate an attack on the honeypot for testing"""
        if target_ip not in self.containers:
            logger.warning(f"No honeypot active for {target_ip}")
            return

        logger.info(f"Simulating {attack_type} attack on honeypot for {target_ip}")
        # This would trigger the honeypot's logging mechanisms