#!/usr/bin/env python3
"""
Agent Beta - The "Illusionist"
Polymorphic Honeypots & Generative Adversarial Engagement

Features:
1. Dynamic polymorphic traps (Docker-based)
2. Generative AI tarpitting (SLM integration via Ollama)
3. Honeytokens (zero-false-positive tripwires)
"""

import os
import json
import time
import requests
import threading
import uuid
import random
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
import subprocess
import logging

# Optional Docker support
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [BETA] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)


class PolymorphicTrapGenerator:
    """Generate and deploy polymorphic honeypots based on threat type"""
    
    TRAP_CONFIGS = {
        'rtsp': {
            'image': 'libvips/libvips:latest',
            'ports': {'554/tcp': 554},
            'env': {
                'SERVICE_TYPE': 'rtsp_camera',
                'TRAP_ID': ''
            },
            'name_prefix': 'honeypot_rtsp'
        },
        'mqtt': {
            'image': 'eclipse-mosquitto:latest',
            'ports': {'1883/tcp': 1883},
            'env': {
                'SERVICE_TYPE': 'mqtt_broker',
                'TRAP_ID': ''
            },
            'name_prefix': 'honeypot_mqtt'
        },
        'ssh': {
            'image': 'cowrie/cowrie:latest',
            'ports': {'22/tcp': 2222},
            'env': {
                'SERVICE_TYPE': 'ssh_server',
                'TRAP_ID': ''
            },
            'name_prefix': 'honeypot_ssh'
        },
        'http': {
            'image': 'kennethreitz/httpbin',
            'ports': {'80/tcp': 8000},
            'env': {
                'SERVICE_TYPE': 'http_server',
                'TRAP_ID': ''
            },
            'name_prefix': 'honeypot_http'
        },
        'telnet': {
            'image': 'cowrie/cowrie:latest',
            'ports': {'23/tcp': 23},
            'env': {
                'SERVICE_TYPE': 'telnet_server',
                'TRAP_ID': ''
            },
            'name_prefix': 'honeypot_telnet'
        },
        'mysql': {
            'image': 'mysql:5.7',
            'ports': {'3306/tcp': 3306},
            'env': {
                'SERVICE_TYPE': 'mysql_database',
                'TRAP_ID': '',
                'MYSQL_ROOT_PASSWORD': 'honeypot_password_123'
            },
            'name_prefix': 'honeypot_mysql'
        }
    }
    
    def __init__(self):
        try:
            if DOCKER_AVAILABLE:
                self.client = docker.from_env()
                logger.info("✓ Docker client initialized")
            else:
                self.client = None
                logger.warning("⚠ Docker not available. Honeypots will be simulated.")
        except Exception as e:
            logger.warning(f"Docker not available: {e}. Honeypots will be simulated.")
            self.client = None
    
    def get_threat_type(self, ports_accessed: set) -> str:
        """Determine threat type from target ports"""
        if not ports_accessed:
            return 'generic'
        
        port_to_service = {
            554: 'rtsp',
            1883: 'mqtt',
            22: 'ssh',
            80: 'http',
            443: 'https',
            23: 'telnet',
            3306: 'mysql',
            5432: 'postgres'
        }
        
        for port in ports_accessed:
            if port in port_to_service:
                return port_to_service[port]
        
        return 'generic'
    
    def deploy_trap(self, target_ip: str, threat_type: str = 'generic', 
                   trap_port: int = None) -> Dict[str, Any]:
        """Deploy a polymorphic honeypot for a specific threat type"""
        
        trap_id = str(uuid.uuid4())[:8]
        config = self.TRAP_CONFIGS.get(threat_type, self.TRAP_CONFIGS['http'])
        
        container_name = f"{config['name_prefix']}_{target_ip.replace('.', '_')}_{trap_id}"
        
        deployment = {
            'trap_id': trap_id,
            'container_name': container_name,
            'target_ip': target_ip,
            'threat_type': threat_type,
            'image': config['image'],
            'status': 'pending',
            'deployed_at': datetime.now().isoformat(),
            'interactions': [],
            'engagement_score': 0,
            'is_active': True
        }
        
        # Try to deploy with Docker
        if self.client:
            try:
                env_vars = config['env'].copy()
                env_vars['TRAP_ID'] = trap_id
                env_vars['TARGET_IP'] = target_ip
                
                ports_mapping = config['ports'].copy()
                if trap_port:
                    ports_mapping = {list(config['ports'].keys())[0]: trap_port}
                
                # Pull image first
                logger.info(f"Pulling Docker image: {config['image']}")
                try:
                    self.client.images.pull(config['image'])
                except:
                    logger.warning(f"Failed to pull {config['image']}, using local cache")
                
                # Deploy container
                container = self.client.containers.run(
                    config['image'],
                    name=container_name,
                    environment=env_vars,
                    ports=ports_mapping,
                    detach=True,
                    remove=True
                )
                
                deployment['status'] = 'active'
                deployment['container_id'] = container.id[:12]
                logger.info(f"✓ Deployed {threat_type} honeypot to {target_ip} (ID: {trap_id})")
                
            except Exception as e:
                logger.warning(f"Docker deployment failed: {e}. Using simulation mode.")
                deployment['status'] = 'simulated'
        else:
            deployment['status'] = 'simulated'
        
        return deployment
    
    def cleanup_trap(self, container_name: str) -> bool:
        """Stop and remove a honeypot container"""
        if not self.client:
            return True
        
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            container.remove()
            logger.info(f"✓ Cleaned up honeypot {container_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cleanup {container_name}: {e}")
            return False


class SLMTarpitter:
    """Small Language Model-based tarpitting for realistic engagement"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "mistral"  # or phi-3, neural-chat
        self.conversation_history = defaultdict(list)
        self.session_id = str(uuid.uuid4())
        self.tarpitting_started = {}
        
        # Verify Ollama is running
        self._verify_ollama()
    
    def _verify_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info("✓ Ollama SLM service is available")
                return True
        except:
            logger.warning("⚠ Ollama SLM service not available. Using template responses.")
        return False
    
    def generate_shell_response(self, attacker_input: str, session_id: str) -> str:
        """Generate realistic shell responses using SLM"""
        
        # Safety check - don't execute anything
        if any(cmd in attacker_input.lower() for cmd in 
               ['rm -rf', 'dd if=', 'fork bomb', ':(){:|:&};:']):
            return "bash: fork bomb: command not found\n"
        
        try:
            # Build prompt for context-aware response
            prompts = {
                'cat /etc/shadow': self._generate_shadow_file,
                'cat /etc/passwd': self._generate_passwd_file,
                'whoami': self._generate_whoami,
                'id': self._generate_id,
                'ls': self._generate_ls,
                'pwd': self._generate_pwd,
                'uname': self._generate_uname,
            }
            
            # Check for exact command matches first
            for cmd, generator in prompts.items():
                if cmd in attacker_input.lower():
                    return generator()
            
            # Try SLM for complex commands
            response = self._query_slm(attacker_input)
            return response if response else self._generate_generic_error(attacker_input)
        
        except Exception as e:
            logger.debug(f"SLM error: {e}")
            return self._generate_generic_error(attacker_input)
    
    def _query_slm(self, prompt: str) -> Optional[str]:
        """Query the SLM for a response"""
        try:
            payload = {
                "model": self.model,
                "prompt": f"You are a honeypot shell simulator. Respond realistically to: {prompt}\nResponse:",
                "stream": False,
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '').strip()[:200]  # Limit output
        except:
            pass
        
        return None
    
    def _generate_shadow_file(self) -> str:
        """Generate a fake /etc/shadow file"""
        fake_hashes = [
            "root:$6$kWk8/6iJ$.Jbk7VWsRzcmOPQZnr7k8O8k7OjKw8jGjZmZ8l8:19000:0:99999:7:::",
            "admin:$6$eKz9Lm2P$3k8J/kL9mZ2.Ox8K9pQ7rMnO8sT3uV4w5xY6zZaAbBbCcDdEeFfGgHh:19000:0:99999:7:::",
            "www-data:!:19000:0:99999:7:::",
            "database:$6$cIvX8e2K$9kLmN7o/8pQrSt9uVwXyZaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuV:19000:0:99999:7:::",
        ]
        return "\n".join(fake_hashes) + "\n"
    
    def _generate_passwd_file(self) -> str:
        """Generate a fake /etc/passwd file"""
        fake_users = [
            "root:x:0:0:root:/root:/bin/bash",
            "admin:x:1000:1000:Administrator:/home/admin:/bin/bash",
            "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin",
            "database:x:1001:1001:Database User:/var/lib/database:/bin/bash",
            "sensor:x:1002:1002:Sensor User:/opt/sensor:/usr/sbin/nologin",
        ]
        return "\n".join(fake_users) + "\n"
    
    def _generate_whoami(self) -> str:
        return "root\n"
    
    def _generate_id(self) -> str:
        return "uid=0(root) gid=0(root) groups=0(root)\n"
    
    def _generate_ls(self) -> str:
        files = ["lost+found  usr  var  tmp  sys  srv  run  root  proc  opt  mnt  media  lib  lib64  home  etc  dev  boot  bin  sbin"]
        return " ".join(files) + "\n"
    
    def _generate_pwd(self) -> str:
        return "/root\n"
    
    def _generate_uname(self) -> str:
        return "Linux honeypot-trap 5.10.0-fake-kernel #1 SMP fake kernel\n"
    
    def _generate_generic_error(self, command: str) -> str:
        return f"bash: {command.split()[0] if command else 'command'}: command not found\n"
    
    def start_tarpitting_session(self, attacker_ip: str, session_id: str) -> str:
        """Initialize a tarpitting session for an attacker"""
        self.tarpitting_started[attacker_ip] = time.time()
        
        fake_banner = f"""
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.10.0-fake)
 
 * For security reasons, this system logs all activities
 * Unauthorized access is prohibited and will be prosecuted by law
 * Last login: {datetime.now().strftime('%a %b %d %H:%M:%S')} from 203.0.113.X
 * System CPU load: {random.uniform(0.5, 2.0):.2f}
 * Memory usage: {random.uniform(30, 80):.1f}%
 
Type 'help' for available commands
root@honeypot-trap:~# """
        
        logger.info(f"🎭 Started tarpitting session with {attacker_ip} (Session: {session_id})")
        return fake_banner
    
    def get_session_duration(self, attacker_ip: str) -> float:
        """Calculate how long an attacker has been engaged"""
        if attacker_ip in self.tarpitting_started:
            return time.time() - self.tarpitting_started[attacker_ip]
        return 0


class HoneyTokenGenerator:
    """Generate and track honeytokens for detection"""
    
    def __init__(self):
        self.honeytokens = {}
        self.token_usage_log = []
        self.data_file = os.path.join(DATA_DIR, 'honeytokens.json')
        self._load_tokens()
    
    def _load_tokens(self):
        """Load existing honeytokens from storage"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.honeytokens = json.load(f)
                    logger.info(f"✓ Loaded {len(self.honeytokens)} honeytokens")
            except Exception as e:
                logger.warning(f"Failed to load honeytokens: {e}")
    
    def generate_aws_key(self) -> Dict[str, str]:
        """Generate mathematically valid but non-functional AWS API key"""
        # AWS Access Keys start with AKIA
        access_key = "AKIA" + ''.join([
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(x) % 36]
            for x in os.urandom(16)
        ])
        
        secret_key = ''.join([
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'[int(x) % 64]
            for x in os.urandom(40)
        ])
        
        return {
            'type': 'aws_api_key',
            'access_key': access_key,
            'secret_key': secret_key,
            'account_id': f"{int.from_bytes(os.urandom(6), 'big')}".zfill(12)[:12],
            'created_at': datetime.now().isoformat()
        }
    
    def generate_db_connection_string(self) -> Dict[str, str]:
        """Generate realistic database connection string"""
        databases = ['admin', 'users', 'financial', 'credentials', 'vault']
        db_name = databases[int.from_bytes(os.urandom(1), 'big') % len(databases)]
        
        fake_password = hashlib.md5(os.urandom(16)).hexdigest()
        
        return {
            'type': 'database_connection',
            'host': '10.0.0.1',
            'port': 5432,
            'database': db_name,
            'username': 'admin',
            'password': fake_password,
            'connection_string': f"postgresql://admin:{fake_password}@10.0.0.1:5432/{db_name}",
            'created_at': datetime.now().isoformat()
        }
    
    def generate_api_token(self) -> Dict[str, str]:
        """Generate realistic API token"""
        prefixes = ['gho_', 'ghp_', 'ghs_', 'ghu_']
        prefix = prefixes[int.from_bytes(os.urandom(1), 'big') % len(prefixes)]
        token = prefix + ''.join([
            '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(x) % 62]
            for x in os.urandom(36)
        ])
        
        return {
            'type': 'api_token',
            'token': token,
            'service': 'GitHub API',
            'scope': ['repo', 'admin:repo_hook', 'admin:org_hook'],
            'created_at': datetime.now().isoformat()
        }
    
    def generate_honeytoken(self, token_type: str = 'random') -> Dict[str, Any]:
        """Generate a honeytoken of specified type"""
        
        generator = {
            'aws': self.generate_aws_key,
            'database': self.generate_db_connection_string,
            'api': self.generate_api_token,
        }
        
        if token_type == 'random':
            token_type = list(generator.keys())[int.from_bytes(os.urandom(1), 'big') % len(generator)]
        
        token_data = generator.get(token_type, generator['api'])()
        token_id = str(uuid.uuid4())
        
        honeytoken = {
            'id': token_id,
            'data': token_data,
            'created_at': datetime.now().isoformat(),
            'triggered': False,
            'trigger_details': None
        }
        
        self.honeytokens[token_id] = honeytoken
        self._save_tokens()
        
        logger.info(f"✨ Generated {token_type} honeytoken (ID: {token_id})")
        return honeytoken
    
    def _save_tokens(self):
        """Save honeytokels to disk"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.honeytokens, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save honeytokens: {e}")
    
    def report_token_usage(self, token_id: str, attacker_ip: str, 
                          timestamp: Optional[str] = None) -> bool:
        """Record a honeytoken usage (zero-false-positive detection)"""
        
        if token_id not in self.honeytokens:
            return False
        
        self.honeytokens[token_id]['triggered'] = True
        self.honeytokens[token_id]['trigger_details'] = {
            'attacker_ip': attacker_ip,
            'discovered_at': timestamp or datetime.now().isoformat(),
            'severity': 'critical'
        }
        
        self._save_tokens()
        
        logger.warning(f"🚨 HONEYTOKEN TRIGGERED! ID: {token_id}, Attacker: {attacker_ip}")
        return True


class AgentBeta:
    """Main Agent Beta class - The Illusionist"""
    
    def __init__(self, alpha_agent=None):
        self.alpha = alpha_agent
        self.trap_generator = PolymorphicTrapGenerator()
        self.slm_tarpitter = SLMTarpitter()
        self.honeytoken_gen = HoneyTokenGenerator()
        
        self.active_honeypots = {}
        self.attacker_sessions = {}
        self.engagement_records = []
        self.running = True
        
        logger.info("✓ Agent Beta initialized (The Illusionist)")
    
    def on_threat_detected(self, threat_data: Dict[str, Any]):
        """Callback from Alpha when threat is detected"""
        
        if not threat_data:
            return
        
        threat_type = threat_data.get('type')
        attacker_ip = threat_data.get('ip')
        attacker_mac = threat_data.get('mac')
        
        logger.info(f"📡 Agent Alpha detected threat: {threat_type} from {attacker_ip}")
        
        # Deploy polymorphic trap based on threat type
        self._deploy_adaptive_trap(attacker_ip, threat_type, attacker_mac)
        
        # Generate and distribute honeytokens
        self._distribute_honeytokens()
    
    def _deploy_adaptive_trap(self, target_ip: str, threat_type: str, mac: str):
        """Deploy an adaptive honeypot based on threat characteristics"""
        
        # Get ports accessed if available
        if self.alpha and mac in self.alpha.devices:
            device = self.alpha.devices[mac]
            ports_accessed = device.get('ports', set())
            detected_threat_type = self.trap_generator.get_threat_type(ports_accessed)
        else:
            detected_threat_type = threat_type
        
        # Deploy trap
        trap = self.trap_generator.deploy_trap(target_ip, detected_threat_type)
        self.active_honeypots[target_ip] = trap
        
        # Start tarpitting session
        session_id = str(uuid.uuid4())[:8]
        tarpitting_prompt = self.slm_tarpitter.start_tarpitting_session(target_ip, session_id)
        
        self.attacker_sessions[target_ip] = {
            'session_id': session_id,
            'trap_id': trap['trap_id'],
            'start_time': time.time(),
            'threat_type': detected_threat_type,
            'banner': tarpitting_prompt,
            'commands': []
        }
        
        logger.info(f"🎭 Deployed {detected_threat_type} trap for {target_ip}")
    
    def _distribute_honeytokens(self):
        """Distribute honeytokens to increase detection"""
        
        # Generate 3-5 honeytokens
        for _ in range(min(5, max(3, len(self.active_honeypots)))):
            self.honeytoken_gen.generate_honeytoken()
    
    def simulate_attacker_interaction(self, attacker_ip: str, command: str) -> str:
        """Simulate interaction with a tarpitted attacker"""
        
        if attacker_ip not in self.attacker_sessions:
            return "Error: No active session\n"
        
        session = self.attacker_sessions[attacker_ip]
        
        # Record the command attempt
        session['commands'].append({
            'command': command,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate response using SLM
        response = self.slm_tarpitter.generate_shell_response(command, session['session_id'])
        
        logger.debug(f"Attacker {attacker_ip} executed: {command}")
        
        return response
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """Get metrics on honeypot engagement"""
        
        metrics = {
            'active_traps': len(self.active_honeypots),
            'active_sessions': len(self.attacker_sessions),
            'total_commands_attempted': sum(len(s['commands']) for s in self.attacker_sessions.values()),
            'honeytokens_generated': len(self.honeytoken_gen.honeytokens),
            'honeytokens_triggered': sum(1 for ht in self.honeytoken_gen.honeytokens.values() if ht['triggered']),
            'average_engagement_time': self._calculate_avg_engagement_time(),
            'threat_intelligence_collected': self._count_collected_intelligence()
        }
        
        return metrics
    
    def _calculate_avg_engagement_time(self) -> float:
        """Calculate average engagement time with attackers"""
        if not self.attacker_sessions:
            return 0
        
        total_time = sum(
            self.slm_tarpitter.get_session_duration(ip)
            for ip in self.attacker_sessions.keys()
        )
        
        return total_time / len(self.attacker_sessions) if self.attacker_sessions else 0
    
    def _count_collected_intelligence(self) -> int:
        """Count amount of threat intelligence collected"""
        count = 0
        for session in self.attacker_sessions.values():
            count += len(session.get('commands', []))
        return count
    
    def cleanup(self, target_ip: str) -> bool:
        """Clean up honeypot for a specific attacker"""
        
        if target_ip in self.active_honeypots:
            trap = self.active_honeypots[target_ip]
            success = self.trap_generator.cleanup_trap(trap['container_name'])
            
            if success:
                self.engagement_records.append({
                    'target_ip': target_ip,
                    'trap_id': trap['trap_id'],
                    'duration': time.time() - self.active_honeypots[target_ip]['deployed_at'],
                    'cleaned_up_at': datetime.now().isoformat()
                })
                
                del self.active_honeypots[target_ip]
            
            if target_ip in self.attacker_sessions:
                del self.attacker_sessions[target_ip]
            
            return success
        
        return False
    
    def get_active_honeypots(self) -> Dict[str, Dict[str, Any]]:
        """Get list of active honeypots"""
        return self.active_honeypots.copy()
    
    def get_engagement_report(self) -> Dict[str, Any]:
        """Generate comprehensive engagement report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.get_engagement_metrics(),
            'active_honeypots': list(self.active_honeypots.keys()),
            'active_sessions': len(self.attacker_sessions),
            'engagement_records': self.engagement_records[-10:]  # Last 10 engagements
        }
        
        # Save report
        report_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(LOG_DIR, f'engagement_report_{report_id}.json')
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"✓ Engagement report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report


if __name__ == "__main__":
    # Test Agent Beta
    beta = AgentBeta()
    
    # Generate some honeytokens
    for _ in range(3):
        beta.honeytoken_gen.generate_honeytoken()
    
    # Simulate threat deployment
    test_threat = {
        'type': 'port_scan',
        'ip': '192.168.1.100',
        'mac': 'aa:bb:cc:dd:ee:ff'
    }
    beta.on_threat_detected(test_threat)
    
    # Show metrics
    metrics = beta.get_engagement_metrics()
    print(json.dumps(metrics, indent=2))
