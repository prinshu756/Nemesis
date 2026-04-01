"""
Database Service Layer
Handles persistence of data to both local SQLite and Neon DB
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.database import DatabaseManager, Device, Alert, TrafficLog, HoneypotInteraction
from core.logging_config import logger

class DatabaseService:
    """Service for managing database operations"""
    
    def __init__(self):
        """Initialize database managers for both local and Neon"""
        # Local SQLite database
        local_db_url = os.getenv('DATABASE_URL', 'sqlite:///./nemesis.db')
        self.local_db = DatabaseManager(local_db_url)
        self.local_db.init_database()
        
        # Neon PostgreSQL database
        neon_db_url = os.getenv('NEON_DATABASE_URL')
        if neon_db_url:
            try:
                self.neon_db = DatabaseManager(neon_db_url)
                self.neon_db.init_database()
                logger.info("✓ Connected to Neon DB")
            except Exception as e:
                logger.warning(f"Neon DB connection failed: {e}. Using local DB only.")
                self.neon_db = None
        else:
            logger.warning("NEON_DATABASE_URL not configured. Using local DB only.")
            self.neon_db = None

    def persist_device(self, device_data: Dict[str, Any]) -> bool:
        """Save device to both databases"""
        try:
            mac_address = device_data.get('mac')
            if not mac_address:
                logger.error("Device data missing MAC address")
                return False

            # Save to local database
            try:
                session = self.local_db.get_session()
                self.local_db.add_or_update_device(
                    session,
                    mac_address,
                    ip_address=device_data.get('ip'),
                    hostname=device_data.get('hostname'),
                    device_type=device_data.get('device_type'),
                    vendor=device_data.get('vendor'),
                    risk_score=device_data.get('risk_score', 0.0),
                    risk_level=device_data.get('risk_level', 'low'),
                    is_active=device_data.get('is_active', True),
                    os_fingerprint=device_data.get('os_fingerprint')
                )
                self.local_db.close_session(session)
                logger.debug(f"✓ Device {mac_address} saved to local DB")
            except Exception as e:
                logger.error(f"Failed to save device to local DB: {e}")

            # Save to Neon database
            if self.neon_db:
                try:
                    session = self.neon_db.get_session()
                    self.neon_db.add_or_update_device(
                        session,
                        mac_address,
                        ip_address=device_data.get('ip'),
                        hostname=device_data.get('hostname'),
                        device_type=device_data.get('device_type'),
                        vendor=device_data.get('vendor'),
                        risk_score=device_data.get('risk_score', 0.0),
                        risk_level=device_data.get('risk_level', 'low'),
                        is_active=device_data.get('is_active', True),
                        os_fingerprint=device_data.get('os_fingerprint')
                    )
                    self.neon_db.close_session(session)
                    logger.debug(f"✓ Device {mac_address} saved to Neon DB")
                except Exception as e:
                    logger.error(f"Failed to save device to Neon DB: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to persist device: {e}")
            return False

    def persist_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Save alert to both databases"""
        try:
            # Save to local database
            try:
                session = self.local_db.get_session()
                self.local_db.add_alert(
                    session,
                    message=alert_data.get('message'),
                    severity=alert_data.get('severity', 'medium'),
                    alert_type=alert_data.get('type', 'generic'),
                    device_mac=alert_data.get('device_mac'),
                    status='open',
                    details=alert_data.get('details', {})
                )
                self.local_db.close_session(session)
                logger.debug(f"✓ Alert saved to local DB")
            except Exception as e:
                logger.error(f"Failed to save alert to local DB: {e}")

            # Save to Neon database
            if self.neon_db:
                try:
                    session = self.neon_db.get_session()
                    self.neon_db.add_alert(
                        session,
                        message=alert_data.get('message'),
                        severity=alert_data.get('severity', 'medium'),
                        alert_type=alert_data.get('type', 'generic'),
                        device_mac=alert_data.get('device_mac'),
                        status='open',
                        details=alert_data.get('details', {})
                    )
                    self.neon_db.close_session(session)
                    logger.debug(f"✓ Alert saved to Neon DB")
                except Exception as e:
                    logger.error(f"Failed to save alert to Neon DB: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to persist alert: {e}")
            return False

    def persist_traffic_log(self, traffic_data: Dict[str, Any]) -> bool:
        """Save traffic log to both databases"""
        try:
            # Save to local database
            try:
                session = self.local_db.get_session()
                self.local_db.add_traffic_log(
                    session,
                    source_ip=traffic_data.get('source_ip'),
                    destination_ip=traffic_data.get('destination_ip'),
                    source_port=traffic_data.get('source_port'),
                    destination_port=traffic_data.get('destination_port'),
                    protocol=traffic_data.get('protocol', 'tcp'),
                    packet_size=traffic_data.get('packet_size', 0),
                    device_id=traffic_data.get('device_id')
                )
                self.local_db.close_session(session)
            except Exception as e:
                logger.error(f"Failed to save traffic log to local DB: {e}")

            # Save to Neon database
            if self.neon_db:
                try:
                    session = self.neon_db.get_session()
                    self.neon_db.add_traffic_log(
                        session,
                        source_ip=traffic_data.get('source_ip'),
                        destination_ip=traffic_data.get('destination_ip'),
                        source_port=traffic_data.get('source_port'),
                        destination_port=traffic_data.get('destination_port'),
                        protocol=traffic_data.get('protocol', 'tcp'),
                        packet_size=traffic_data.get('packet_size', 0),
                        device_id=traffic_data.get('device_id')
                    )
                    self.neon_db.close_session(session)
                except Exception as e:
                    logger.error(f"Failed to save traffic log to Neon DB: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to persist traffic log: {e}")
            return False

    def persist_honeypot_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Save honeypot interaction to both databases"""
        try:
            # Save to local database
            try:
                session = self.local_db.get_session()
                interaction = HoneypotInteraction(
                    ip_address=interaction_data.get('ip_address'),
                    threat_type=interaction_data.get('threat_type'),
                    attack_type=interaction_data.get('attack_type'),
                    honeypot_type=interaction_data.get('honeypot_type'),
                    severity=interaction_data.get('severity', 'medium'),
                    details=interaction_data.get('details', {})
                )
                session.add(interaction)
                session.commit()
                self.local_db.close_session(session)
            except Exception as e:
                logger.error(f"Failed to save honeypot interaction to local DB: {e}")

            # Save to Neon database
            if self.neon_db:
                try:
                    session = self.neon_db.get_session()
                    interaction = HoneypotInteraction(
                        ip_address=interaction_data.get('ip_address'),
                        threat_type=interaction_data.get('threat_type'),
                        attack_type=interaction_data.get('attack_type'),
                        honeypot_type=interaction_data.get('honeypot_type'),
                        severity=interaction_data.get('severity', 'medium'),
                        details=interaction_data.get('details', {})
                    )
                    session.add(interaction)
                    session.commit()
                    self.neon_db.close_session(session)
                except Exception as e:
                    logger.error(f"Failed to save honeypot interaction to Neon DB: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to persist honeypot interaction: {e}")
            return False

    def get_devices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve devices from local database"""
        try:
            session = self.local_db.get_session()
            devices = session.query(Device).limit(limit).all()
            self.local_db.close_session(session)
            
            return [dev.to_dict() for dev in devices]
        except Exception as e:
            logger.error(f"Failed to retrieve devices: {e}")
            return []

    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve alerts from local database"""
        try:
            session = self.local_db.get_session()
            alerts = session.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
            self.local_db.close_session(session)
            
            return [
                {
                    'id': alert.id,
                    'message': alert.message,
                    'severity': alert.severity,
                    'type': alert.alert_type,
                    'device_mac': alert.device_mac,
                    'timestamp': alert.timestamp.isoformat() if alert.timestamp else None,
                    'status': alert.status
                }
                for alert in alerts
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve alerts: {e}")
            return []

    def get_traffic_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve traffic logs from local database"""
        try:
            session = self.local_db.get_session()
            logs = session.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).limit(limit).all()
            self.local_db.close_session(session)
            
            return [
                {
                    'id': log.id,
                    'source_ip': log.source_ip,
                    'destination_ip': log.destination_ip,
                    'source_port': log.source_port,
                    'destination_port': log.destination_port,
                    'protocol': log.protocol,
                    'packet_size': log.packet_size,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None
                }
                for log in logs
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve traffic logs: {e}")
            return []

    def get_honeypot_interactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve honeypot interactions from local database"""
        try:
            session = self.local_db.get_session()
            interactions = session.query(HoneypotInteraction).order_by(HoneypotInteraction.timestamp.desc()).limit(limit).all()
            self.local_db.close_session(session)
            
            return [
                {
                    'id': inter.id,
                    'ip_address': inter.ip_address,
                    'threat_type': inter.threat_type,
                    'attack_type': inter.attack_type,
                    'honeypot_type': inter.honeypot_type,
                    'severity': inter.severity,
                    'timestamp': inter.timestamp.isoformat() if inter.timestamp else None
                }
                for inter in interactions
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve honeypot interactions: {e}")
            return []

# Global database service instance
db_service = DatabaseService()
