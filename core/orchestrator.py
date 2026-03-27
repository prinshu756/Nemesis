import asyncio
from core.state_manager import StateManager
from core.risk_engine import RiskEngine
from core.policy_engine import PolicyEngine
from core.logging_config import logger
from core.config import config

from agents.alpha import AgentAlpha
from agents.beta import AgentBeta
from agents.gamma import AgentGamma

class NemesisOrchestrator:
    def __init__(self):
        logger.info("Initializing Nemesis Orchestrator...")

        # Lazy initialization - agents will be initialized when first accessed
        self._alpha = None
        self._beta = None
        self._gamma = None

        self.state = StateManager()
        self.risk_engine = RiskEngine()
        self.policy = PolicyEngine()

        self.running = True
        self.alerts = []
        self.response_actions = []

        logger.info("Nemesis Orchestrator initialized successfully")

    @property
    def alpha(self):
        if self._alpha is None:
            try:
                self._alpha = AgentAlpha()
                logger.info("Agent Alpha initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Agent Alpha: {e}")
                self._alpha = None
        return self._alpha

    @property
    def beta(self):
        if self._beta is None:
            try:
                self._beta = AgentBeta()
                logger.info("Agent Beta initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Agent Beta: {e}")
                self._beta = None
        return self._beta

    @property
    def gamma(self):
        if self._gamma is None:
            try:
                self._gamma = AgentGamma()
                logger.info("Agent Gamma initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Agent Gamma: {e}")
                self._gamma = None
        return self._gamma

    async def run(self):
        """Main orchestration loop with enhanced error handling"""
        logger.info("Starting Nemesis orchestration loop")

        try:
            # Start Alpha's packet capture in background thread
            asyncio.create_task(asyncio.to_thread(self._run_alpha_capture))

            # Main monitoring loop
            while self.running:
                try:
                    await self._process_devices()
                    await self._cleanup_expired_policies()
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(5)  # Wait longer on error

        except Exception as e:
            logger.critical(f"Critical error in orchestrator: {e}")
            await self._emergency_shutdown()

    async def _process_devices(self):
        """Process all discovered devices for threats and responses"""
        if not self.alpha:
            logger.warning("Agent Alpha not available, skipping device processing")
            return

        for mac, device in list(self.alpha.devices.items()):
            try:
                # Update state
                self.state.update_device(mac, device)

                # Compute risk
                risk = self.risk_engine.compute_risk(device)

                # Determine action based on risk
                action = self._determine_action(risk, device)

                # Execute response
                if action:
                    await self._execute_response(mac, device, action)

                # Check for alerts
                alerts = self._check_for_alerts(device, risk)
                for alert in alerts:
                    self._add_alert(alert)

            except Exception as e:
                logger.error(f"Error processing device {mac}: {e}")

    def _determine_action(self, risk_score, device):
        """Determine appropriate response action based on risk and context"""
        thresholds = config.get('risk_thresholds', {})

        if risk_score >= thresholds.get('high', 80):
            return "isolate"
        elif risk_score >= thresholds.get('medium', 50):
            # Check device context for honeypot vs isolation
            if self._should_deploy_honeypot(device):
                return "honeypot"
            else:
                return "isolate"
        elif risk_score >= thresholds.get('low', 20):
            return "monitor"

        return None

    def _should_deploy_honeypot(self, device):
        """Determine if honeypot deployment is appropriate"""
        # Deploy honeypots for suspicious but not critical threats
        suspicious_indicators = [
            device.get('vm_detected', False),
            len(device.get('ports', set())) > 10,
            device.get('packet_count', 0) > 500
        ]

        return sum(suspicious_indicators) >= 2

    async def _execute_response(self, mac, device, action):
        """Execute the determined response action"""
        try:
            if action == "isolate":
                if self.gamma:
                    policy = self._select_isolation_policy(device)
                    self.gamma.isolate_device(mac, policy)
                    self.response_actions.append({
                        'timestamp': asyncio.get_event_loop().time(),
                        'mac': mac,
                        'action': 'isolate',
                        'policy': policy
                    })
                else:
                    logger.warning("Agent Gamma not available for isolation")

            elif action == "honeypot":
                if self.beta:
                    threat_type = self._classify_threat(device)
                    container = self.beta.deploy_honeypot(device.get('ip'), threat_type)
                    if container:
                        self.response_actions.append({
                            'timestamp': asyncio.get_event_loop().time(),
                            'mac': mac,
                            'action': 'honeypot',
                            'container': container,
                            'threat_type': threat_type
                        })
                else:
                    logger.warning("Agent Beta not available for honeypot deployment")

            logger.info(f"Executed {action} for device {mac}")

        except Exception as e:
            logger.error(f"Failed to execute {action} for {mac}: {e}")

    def _select_isolation_policy(self, device):
        """Select appropriate isolation policy based on device context"""
        if device.get('vm_detected'):
            return "limited_services"  # Allow DNS for VMs
        elif device.get('device_type') == 'IoT':
            return "lateral_block"  # Block LAN but allow internet
        else:
            return "full_isolation"

    def _classify_threat(self, device):
        """Classify the type of threat for honeypot selection"""
        if 22 in device.get('ports', set()):
            return "ssh"
        elif 80 in device.get('ports', set()) or 443 in device.get('ports', set()):
            return "web"
        elif 21 in device.get('ports', set()):
            return "ftp"
        else:
            return "generic"

    def _check_for_alerts(self, device, risk_score):
        """Check for conditions that should trigger alerts"""
        alerts = []

        if risk_score >= 80:
            alerts.append({
                'level': 'critical',
                'message': f"High-risk device detected: {device.get('mac')}",
                'device': device,
                'risk_score': risk_score
            })

        # Check for rapid port scanning
        ports = device.get('ports', set())
        if len(ports) > 20:
            alerts.append({
                'level': 'warning',
                'message': f"Port scanning detected: {device.get('mac')} scanned {len(ports)} ports",
                'device': device
            })

        return alerts

    def _add_alert(self, alert):
        """Add alert to the system"""
        alert['timestamp'] = asyncio.get_event_loop().time()
        self.alerts.append(alert)
        self.state.add_alert(alert)

        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        logger.warning(f"Alert: {alert['message']}")

    async def _cleanup_expired_policies(self):
        """Clean up expired policies and honeypots"""
        current_time = asyncio.get_event_loop().time()

        # Clean up old response actions (older than 1 hour)
        self.response_actions = [
            action for action in self.response_actions
            if current_time - action['timestamp'] < 3600
        ]

        # Clean up honeypots for inactive IPs
        active_ips = {device.get('ip') for device in self.alpha.devices.values() if device.get('ip')}
        honeypots = self.beta.get_active_honeypots()

        for ip in honeypots:
            if ip not in active_ips:
                self.beta.cleanup_honeypot(ip)
                logger.info(f"Cleaned up honeypot for inactive IP: {ip}")

    def _run_alpha_capture(self):
        """Run Alpha's packet capture (blocking)"""
        try:
            logger.info("Starting Alpha packet capture")
            self.alpha.start()
        except KeyboardInterrupt:
            logger.info("Alpha capture interrupted by user")
        except Exception as e:
            logger.error(f"Alpha capture failed: {e}")
        finally:
            self.running = False

    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        logger.critical("Initiating emergency shutdown")

        try:
            # Stop all honeypots
            honeypots = self.beta.get_active_honeypots()
            for ip in honeypots:
                self.beta.cleanup_honeypot(ip)

            # Cleanup Gamma policies
            self.gamma.cleanup()

            logger.info("Emergency shutdown completed")

        except Exception as e:
            logger.error(f"Error during emergency shutdown: {e}")

    def get_status(self):
        """Get comprehensive system status"""
        status = {
            'alpha_devices': len(self.alpha.devices) if self.alpha else 0,
            'beta_honeypots': len(self.beta.get_active_honeypots()) if self.beta else 0,
            'gamma_policies': self.gamma.get_segmentation_status() if self.gamma else {'policies': {}, 'ebpf_attached': False},
            'alerts_count': len(self.alerts),
            'response_actions_count': len(self.response_actions),
            'system_running': self.running,
            'agents_status': {
                'alpha': self.alpha is not None,
                'beta': self.beta is not None,
                'gamma': self.gamma is not None
            }
        }
        return status