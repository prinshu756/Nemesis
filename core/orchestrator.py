import asyncio
from datetime import datetime, timedelta
from core.state_manager import StateManager
from core.risk_engine import RiskEngine
from core.policy_engine import PolicyEngine
from core.logging_config import logger
from core.config import config, db_manager, settings
from core.database import Device, Alert, TrafficLog, HoneypotInteraction, SystemMetric

from agents.alpha import AgentAlpha
from agents.beta import AgentBeta
from agents.gamma import AgentGamma

class NemesisOrchestrator:
    def __init__(self):
        logger.info("Initializing Nemesis Orchestrator...")

        # Database session
        self.db_session = db_manager.get_session()

        # Lazy initialization - agents will be initialized when first accessed
        self._alpha = None
        self._beta = None
        self._gamma = None

        self.state = StateManager()
        self.risk_engine = RiskEngine()
        self.policy = PolicyEngine()

        self.running = True
        self.device_cache = {}  # In-memory cache for performance

        logger.info("Nemesis Orchestrator initialized successfully")

    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db_session'):
            db_manager.close_session(self.db_session)

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
                # Store/update device in database
                await self._store_device(mac, device)

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
                    await self._store_alert(alert)

            except Exception as e:
                logger.error(f"Error processing device {mac}: {e}")

    async def _store_device(self, mac, device_data):
        """Store or update device information in database"""
        try:
            # Check if device exists
            device = self.db_session.query(Device).filter_by(mac_address=mac).first()

            if device:
                # Update existing device
                device.ip_address = device_data.get('ip')
                device.hostname = device_data.get('hostname')
                device.device_type = device_data.get('device_type')
                device.os_info = device_data.get('os_info')
                device.vendor = device_data.get('vendor')
                device.ports = list(device_data.get('ports', set()))
                device.services = device_data.get('services', {})
                device.last_seen = datetime.utcnow()
                device.risk_score = device_data.get('risk_score', 0)
                device.isolation_status = device_data.get('isolation_status', 'active')
                device.vm_detected = device_data.get('vm_detected', False)
                device.packet_count = device_data.get('packet_count', 0)
            else:
                # Create new device
                device = Device(
                    mac_address=mac,
                    ip_address=device_data.get('ip'),
                    hostname=device_data.get('hostname'),
                    device_type=device_data.get('device_type'),
                    os_info=device_data.get('os_info'),
                    vendor=device_data.get('vendor'),
                    ports=list(device_data.get('ports', set())),
                    services=device_data.get('services', {}),
                    risk_score=device_data.get('risk_score', 0),
                    isolation_status=device_data.get('isolation_status', 'active'),
                    vm_detected=device_data.get('vm_detected', False),
                    packet_count=device_data.get('packet_count', 0)
                )
                self.db_session.add(device)

            self.db_session.commit()
            logger.debug(f"Stored device {mac} in database")

        except Exception as e:
            logger.error(f"Failed to store device {mac}: {e}")
            self.db_session.rollback()

    async def _store_alert(self, alert_data):
        """Store alert in database"""
        try:
            alert = Alert(
                level=alert_data.get('level', 'info'),
                message=alert_data['message'],
                device_mac=alert_data.get('device', {}).get('mac'),
                risk_score=alert_data.get('risk_score'),
                details=alert_data
            )
            self.db_session.add(alert)
            self.db_session.commit()

            # Keep in-memory cache for quick access
            self.state.add_alert(alert_data)
            logger.warning(f"Alert stored: {alert_data['message']}")

        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
            self.db_session.rollback()

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

                    # Store isolation action
                    await self._store_response_action(mac, device, 'isolate', {'policy': policy})
                else:
                    logger.warning("Agent Gamma not available for isolation")

            elif action == "honeypot":
                if self.beta:
                    threat_type = self._classify_threat(device)
                    container = self.beta.deploy_honeypot(device.get('ip'), threat_type)
                    if container:
                        # Store honeypot deployment
                        await self._store_honeypot_interaction(device.get('ip'), threat_type, container, 'deployed')
                        await self._store_response_action(mac, device, 'honeypot', {
                            'container': container,
                            'threat_type': threat_type
                        })
                else:
                    logger.warning("Agent Beta not available for honeypot deployment")

            logger.info(f"Executed {action} for device {mac}")

        except Exception as e:
            logger.error(f"Failed to execute {action} for {mac}: {e}")

    async def _store_response_action(self, mac, device, action_type, details):
        """Store response action in database"""
        try:
            # Store as system metric for tracking
            metric = SystemMetric(
                metric_type='response_action',
                metric_name=f"{action_type}_{mac}",
                value=1.0,
                details={
                    'mac_address': mac,
                    'device_ip': device.get('ip'),
                    'action_type': action_type,
                    'details': details
                }
            )
            self.db_session.add(metric)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"Failed to store response action: {e}")
            self.db_session.rollback()

    async def _store_honeypot_interaction(self, ip, threat_type, container_id, interaction_type):
        """Store honeypot interaction in database"""
        try:
            interaction = HoneypotInteraction(
                ip_address=ip,
                threat_type=threat_type,
                container_id=container_id,
                interaction_type=interaction_type,
                details={'threat_type': threat_type, 'container': container_id}
            )
            self.db_session.add(interaction)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"Failed to store honeypot interaction: {e}")
            self.db_session.rollback()

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

    async def _store_alert(self, alert_data):
        """Store alert in database"""
        try:
            alert = Alert(
                level=alert_data.get('level', 'info'),
                message=alert_data['message'],
                device_mac=alert_data.get('device', {}).get('mac'),
                risk_score=alert_data.get('risk_score'),
                details=alert_data
            )
            self.db_session.add(alert)
            self.db_session.commit()

            # Keep in-memory cache for quick access
            self.state.add_alert(alert_data)
            logger.warning(f"Alert stored: {alert_data['message']}")

        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
            self.db_session.rollback()

    async def _cleanup_expired_policies(self):
        """Clean up expired policies and honeypots"""
        try:
            current_time = datetime.utcnow()

            # Clean up honeypots for inactive IPs
            active_ips = {device.get('ip') for device in self.alpha.devices.values() if device.get('ip')}
            honeypots = self.beta.get_active_honeypots() if self.beta else []

            for ip in honeypots:
                if ip not in active_ips:
                    self.beta.cleanup_honeypot(ip)
                    # Mark honeypot as cleaned up in database
                    await self._store_honeypot_interaction(ip, 'unknown', None, 'cleanup')
                    logger.info(f"Cleaned up honeypot for inactive IP: {ip}")

            # Clean up old database records (older than 30 days)
            cutoff_date = current_time - timedelta(days=30)

            # Clean old traffic logs
            old_traffic = self.db_session.query(TrafficLog).filter(TrafficLog.timestamp < cutoff_date).delete()
            if old_traffic > 0:
                logger.info(f"Cleaned up {old_traffic} old traffic log entries")

            # Clean old system metrics
            old_metrics = self.db_session.query(SystemMetric).filter(SystemMetric.timestamp < cutoff_date).delete()
            if old_metrics > 0:
                logger.info(f"Cleaned up {old_metrics} old system metric entries")

            self.db_session.commit()

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            self.db_session.rollback()

    async def _store_traffic_log(self, packet_data):
        """Store traffic log entry"""
        try:
            log_entry = TrafficLog(
                source_ip=packet_data.get('src_ip'),
                destination_ip=packet_data.get('dst_ip'),
                source_port=packet_data.get('src_port'),
                destination_port=packet_data.get('dst_port'),
                protocol=packet_data.get('protocol'),
                packet_size=packet_data.get('size', 0),
                flags=packet_data.get('flags'),
                details=packet_data
            )
            self.db_session.add(log_entry)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"Failed to store traffic log: {e}")
            self.db_session.rollback()

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
            # Get database statistics
            device_count = self.db_session.query(Device).count()
            alert_count = self.db_session.query(Alert).count()
            traffic_count = self.db_session.query(TrafficLog).count()
            honeypot_count = self.db_session.query(HoneypotInteraction).filter_by(interaction_type='deployed').count()
            metric_count = self.db_session.query(SystemMetric).count()

            status = {
                'alpha_devices': len(self.alpha.devices) if self.alpha else 0,
                'beta_honeypots': len(self.beta.get_active_honeypots()) if self.beta else 0,
                'gamma_policies': self.gamma.get_segmentation_status() if self.gamma else {'policies': {}, 'ebpf_attached': False},
                'database_stats': {
                    'devices': device_count,
                    'alerts': alert_count,
                    'traffic_logs': traffic_count,
                    'honeypot_interactions': honeypot_count,
                    'system_metrics': metric_count
                },
                'system_running': self.running,
                'agents_status': {
                    'alpha': self.alpha is not None,
                    'beta': self.beta is not None,
                    'gamma': self.gamma is not None
                },
                'timestamp': datetime.utcnow().isoformat()
            }

            return status

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                'error': str(e),
                'system_running': self.running,
                'agents_status': {
                    'alpha': self.alpha is not None,
                    'beta': self.beta is not None,
                    'gamma': self.gamma is not None
                },
                'timestamp': datetime.utcnow().isoformat()
            }

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
                'timestamp': alert.timestamp.isoformat(),
                'details': alert.details
            } for alert in alerts]

        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []

    def get_device_stats(self):
        """Get device statistics from database"""
        try:
            devices = self.db_session.query(Device).all()
            stats = {
                'total_devices': len(devices),
                'by_type': {},
                'by_risk_level': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                'isolated_devices': 0,
                'vm_devices': 0
            }

            for device in devices:
                # Count by type
                dev_type = device.device_type or 'unknown'
                stats['by_type'][dev_type] = stats['by_type'].get(dev_type, 0) + 1

                # Count by risk level
                risk = device.risk_score or 0
                if risk >= 80:
                    stats['by_risk_level']['critical'] += 1
                elif risk >= 60:
                    stats['by_risk_level']['high'] += 1
                elif risk >= 40:
                    stats['by_risk_level']['medium'] += 1
                else:
                    stats['by_risk_level']['low'] += 1

                # Count isolated and VM devices
                if device.isolation_status != 'active':
                    stats['isolated_devices'] += 1
                if device.vm_detected:
                    stats['vm_devices'] += 1

            return stats

        except Exception as e:
            logger.error(f"Error getting device stats: {e}")
            return {}