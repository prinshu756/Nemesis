import asyncio
from datetime import datetime, timedelta
from core.state_manager import StateManager
from core.risk_engine import RiskEngine
from core.policy_engine import PolicyEngine
from core.logging_config import logger
from core.config import config
from core.database import db_manager, Device, Alert, TrafficLog, HoneypotInteraction, SystemMetric

from agents.alpha.alpha import AgentAlpha
from agents.beta import AgentBeta
from agents.gamma.gamma import AgentGamma

class NemesisOrchestrator:
    def __init__(self):
        logger.info("Initializing Nemesis Orchestrator...")

        # Initialize database
        db_manager.init_database()
        self.db_session = db_manager.get_session()

        # Lazy initialization - agents will be initialized when first accessed
        self._alpha = None
        self._beta = None
        self._gamma = None

        self.state = StateManager()
        self.risk_engine = RiskEngine()
        self.policy = PolicyEngine()

        self.running = True

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
                # Pass alpha agent instance to beta for integration
                self._beta = AgentBeta(alpha_agent=self.alpha)
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
            # Register Beta as threat callback from Alpha
            if self.alpha and self.beta:
                self.alpha.add_threat_callback(self.beta.on_threat_detected)
                logger.info("✓ Registered Agent Beta as threat callback for Agent Alpha")
            
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
                # Compute risk
                risk = self.risk_engine.compute_risk(device)
                
                # Determine risk level
                thresholds = config.get('risk_thresholds', {})
                if risk >= thresholds.get('high', 80):
                    risk_level = 'critical'
                elif risk >= thresholds.get('medium', 50):
                    risk_level = 'high'
                elif risk >= thresholds.get('low', 20):
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                # Enrich device data with frontend-required fields
                enriched_device = {
                    **device,
                    'mac': mac,
                    'risk_score': risk,
                    'risk_level': risk_level,
                    'status': 'online',  # Default status
                    'isolation_status': 'normal',  # Default isolation status
                    'health': max(0, 100 - risk),  # Health inversely proportional to risk
                    'power_level': 85,  # Placeholder for device power/battery level
                    'hostname': f"Device-{mac.split(':')[-2:][:2][-1].upper()}",  # Generate hostname from MAC
                    'device_type': device.get('fingerprint', 'Unknown').split('(')[0].strip() if device.get('fingerprint') else 'Unknown',
                    'is_mobile': device.get('is_mobile', False),
                    'mobile_device_type': device.get('mobile_device_type'),
                    'id': mac  # For backward compatibility
                }
                
                # Update state
                self.state.update_device(mac, enriched_device)

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
                    logger.info(f"Isolation executed for {mac} with policy {policy}")
                else:
                    logger.warning("Agent Gamma not available for isolation")

            elif action == "honeypot":
                if self.beta:
                    threat_type = self._classify_threat(device)
                    container = self.beta.deploy_honeypot(device.get('ip'), threat_type)
                    if container:
                        logger.info(f"Honeypot deployed for {device.get('ip')} ({threat_type})")
                        # Store honeypot interaction
                        self.store_honeypot_interaction(
                            device.get('ip'),
                            threat_type,
                            threat_type
                        )
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
        """Add alert to the system and database"""
        try:
            # Store to database
            db_alert = Alert(
                level=alert.get('level', 'warning'),
                message=alert.get('message', ''),
                device_mac=alert.get('device', {}).get('mac'),
                risk_score=alert.get('risk_score'),
                details=alert
            )
            self.db_session.add(db_alert)
            self.db_session.commit()
            
            # Also add to state for real-time access
            self.state.add_alert(alert)
            logger.warning(f"Alert: {alert.get('message', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
            self.db_session.rollback()

    async def _cleanup_expired_policies(self):
        """Clean up expired policies and honeypots"""
        try:
            # Only cleanup if Alpha is initialized
            if not self.alpha or not self.alpha.devices:
                return
                
            # Clean up honeypots for inactive IPs
            active_ips = {device.get('ip') for device in self.alpha.devices.values() if device.get('ip')}
            
            # Only cleanup if Beta is initialized
            if self.beta:
                honeypots = self.beta.get_active_honeypots()
                for ip in honeypots:
                    if ip not in active_ips:
                        self.beta.cleanup_honeypot(ip)
                        logger.info(f"Cleaned up honeypot for inactive IP: {ip}")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

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
        try:
            # Count database entries
            device_count = self.db_session.query(Device).count()
            alert_count = self.db_session.query(Alert).count()
            traffic_count = self.db_session.query(TrafficLog).count()
            honeypot_count = self.db_session.query(HoneypotInteraction).count()
            
            status = {
                'alpha_devices': len(self.alpha.devices) if self.alpha else 0,
                'beta_honeypots': len(self.beta.get_active_honeypots()) if self.beta else 0,
                'gamma_policies': self.gamma.get_segmentation_status() if self.gamma else {'policies': {}, 'ebpf_attached': False},
                'database': {
                    'devices': device_count,
                    'alerts': alert_count,
                    'traffic_logs': traffic_count,
                    'honeypot_interactions': honeypot_count
                },
                'system_running': self.running,
                'agents_status': {
                    'alpha': self.alpha is not None,
                    'beta': self.beta is not None,
                    'gamma': self.gamma is not None
                }
            }
            return status
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {'error': str(e), 'system_running': self.running}

    def store_device_data(self, mac, device_info):
        """Store device information in database"""
        try:
            device = self.db_session.query(Device).filter_by(mac_address=mac).first()
            
            if device:
                device.ip_address = device_info.get('ip')
                device.hostname = device_info.get('hostname')
                device.device_type = device_info.get('device_type')
                device.os_fingerprint = device_info.get('os_fingerprint')
                device.vendor = device_info.get('vendor')
                device.packet_count = device_info.get('packet_count', 0)
                device.risk_score = device_info.get('risk_score', 0)
                device.ports = device_info.get('ports', {})
                device.services = device_info.get('services', {})
            else:
                device = Device(
                    mac_address=mac,
                    ip_address=device_info.get('ip'),
                    hostname=device_info.get('hostname'),
                    device_type=device_info.get('device_type'),
                    os_fingerprint=device_info.get('os_fingerprint'),
                    vendor=device_info.get('vendor'),
                    packet_count=device_info.get('packet_count', 0),
                    risk_score=device_info.get('risk_score', 0),
                    ports=device_info.get('ports', {}),
                    services=device_info.get('services', {})
                )
                self.db_session.add(device)
            
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing device data: {e}")
            self.db_session.rollback()

    def store_traffic_log(self, src_ip, dst_ip, src_port, dst_port, protocol, packet_size=0, flags=''):
        """Store network traffic in database"""
        try:
            traffic = TrafficLog(
                source_ip=src_ip,
                src_ip=src_ip,
                destination_ip=dst_ip,
                dst_ip=dst_ip,
                source_port=src_port,
                src_port=src_port,
                destination_port=dst_port,
                dst_port=dst_port,
                protocol=protocol,
                packet_size=packet_size,
                flags=flags
            )
            self.db_session.add(traffic)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing traffic log: {e}")
            self.db_session.rollback()

    def store_honeypot_interaction(self, ip, honeypot_type, threat_type, attack_payload=''):
        """Store honeypot detection event in database"""
        try:
            interaction = HoneypotInteraction(
                ip_address=ip,
                src_ip=ip,
                honeypot_type=honeypot_type,
                threat_type=threat_type,
                attack_type=threat_type,
                payload=attack_payload,
                event_type='detection',
                interaction_type='detected'
            )
            self.db_session.add(interaction)
            self.db_session.commit()
            logger.info(f"Stored honeypot interaction: {threat_type} from {ip}")
            
        except Exception as e:
            logger.error(f"Error storing honeypot interaction: {e}")
            self.db_session.rollback()

    def store_system_metric(self, metric_type, metric_name, value, unit=''):
        """Store system metric in database"""
        try:
            metric = SystemMetric(
                metric_type=metric_type,
                metric_name=metric_name,
                value=value,
                unit=unit
            )
            self.db_session.add(metric)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing system metric: {e}")
            self.db_session.rollback()

    def get_recent_alerts(self, limit=50):
        """Get recent alerts from database"""
        try:
            alerts = self.db_session.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
            return [{
                'id': alert.id,
                'level': alert.level,
                'message': alert.message,
                'device_mac': alert.device_mac,
                'risk_score': alert.risk_score,
                'timestamp': alert.timestamp.isoformat() if alert.timestamp else None,
                'details': alert.details
            } for alert in alerts]
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []