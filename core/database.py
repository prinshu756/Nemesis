"""
Nemesis Database Models
Comprehensive data persistence for SOC operations
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool
import json

Base = declarative_base()

# Association tables for many-to-many relationships
device_vulnerabilities = Table('device_vulnerabilities', Base.metadata,
    Column('device_id', Integer, ForeignKey('devices.id')),
    Column('vulnerability_id', Integer, ForeignKey('vulnerabilities.id'))
)

device_alerts = Table('device_alerts', Base.metadata,
    Column('device_id', Integer, ForeignKey('devices.id')),
    Column('alert_id', Integer, ForeignKey('alerts.id'))
)

class Device(Base):
    """Network device information and state"""
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    mac_address = Column(String(17), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), index=True)  # IPv4/IPv6 support
    hostname = Column(String(255))
    device_type = Column(String(100))
    os_fingerprint = Column(String(255))
    vendor = Column(String(100))

    # Network characteristics
    ttl = Column(Integer)
    tcp_window_size = Column(Integer)
    mtu = Column(Integer)

    # Risk assessment
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default='low')  # low, medium, high, critical
    threat_level = Column(String(20), default='normal')

    # Behavioral analysis
    packet_count = Column(Integer, default=0)
    bytes_transferred = Column(Integer, default=0)
    connection_count = Column(Integer, default=0)
    port_scan_detected = Column(Boolean, default=False)
    anomalous_behavior = Column(JSON)  # Store behavioral anomalies

    # Device state
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    isolation_status = Column(String(20), default='normal')  # normal, isolated, quarantined

    # Relationships
    vulnerabilities = relationship("Vulnerability", secondary=device_vulnerabilities, back_populates="devices")
    alerts = relationship("Alert", secondary=device_alerts, back_populates="devices")
    traffic_logs = relationship("TrafficLog", back_populates="device")
    honeypot_interactions = relationship("HoneypotInteraction", back_populates="device")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'mac': self.mac_address,
            'ip': self.ip_address,
            'hostname': self.hostname,
            'device_type': self.device_type,
            'os_fingerprint': self.os_fingerprint,
            'vendor': self.vendor,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'threat_level': self.threat_level,
            'packet_count': self.packet_count,
            'bytes_transferred': self.bytes_transferred,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'is_active': self.is_active,
            'isolation_status': self.isolation_status
        }

class Vulnerability(Base):
    """CVE and vulnerability information"""
    __tablename__ = 'vulnerabilities'

    id = Column(Integer, primary_key=True)
    cve_id = Column(String(20), unique=True, index=True)
    title = Column(String(500))
    description = Column(Text)
    severity = Column(String(20))  # low, medium, high, critical
    cvss_score = Column(Float)
    affected_products = Column(JSON)  # List of affected software/products
    published_date = Column(DateTime)
    last_modified = Column(DateTime)

    # Relationships
    devices = relationship("Device", secondary=device_vulnerabilities, back_populates="vulnerabilities")

class Alert(Base):
    """Security alerts and anomalies"""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)
    alert_id = Column(String(50), unique=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    alert_type = Column(String(50))  # anomaly, intrusion, malware, etc.
    source = Column(String(50))  # alpha, beta, gamma, ai

    # Alert data
    raw_data = Column(JSON)  # Original alert data
    enriched_data = Column(JSON)  # AI-enriched information

    # Status and response
    status = Column(String(20), default='new')  # new, investigating, resolved, false_positive
    assigned_to = Column(String(100))
    response_actions = Column(JSON)  # List of actions taken
    resolution_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    devices = relationship("Device", secondary=device_alerts, back_populates="alerts")

class TrafficLog(Base):
    """Network traffic logging"""
    __tablename__ = 'traffic_logs'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'), index=True)

    # Packet information
    src_ip = Column(String(45))
    dst_ip = Column(String(45))
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String(10))  # TCP, UDP, ICMP, etc.

    # Traffic metrics
    packet_size = Column(Integer)
    packet_count = Column(Integer, default=1)
    bytes_transferred = Column(Integer)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration = Column(Float)  # Connection duration in seconds

    # Classification
    traffic_type = Column(String(50))  # normal, suspicious, malicious
    classification_reason = Column(String(200))

    # Relationships
    device = relationship("Device", back_populates="traffic_logs")

class HoneypotInteraction(Base):
    """Honeypot detection events"""
    __tablename__ = 'honeypot_interactions'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'), index=True)
    honeypot_id = Column(String(100), index=True)
    honeypot_type = Column(String(50))  # cowrie, opencanary, etc.

    # Interaction details
    src_ip = Column(String(45))
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String(10))

    # Attack information
    attack_type = Column(String(100))  # ssh_brute_force, port_scan, etc.
    payload = Column(Text)  # Command or payload data
    credentials_used = Column(JSON)  # Username/password attempts

    # Response
    response_sent = Column(Text)
    session_log = Column(Text)  # Full session transcript

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(20), default='medium')
    blocked = Column(Boolean, default=True)

    # Relationships
    device = relationship("Device", back_populates="honeypot_interactions")

class SystemMetric(Base):
    """System performance and health metrics"""
    __tablename__ = 'system_metrics'

    id = Column(Integer, primary_key=True)
    metric_type = Column(String(50), index=True)  # cpu, memory, network, etc.
    metric_name = Column(String(100))
    value = Column(Float)
    unit = Column(String(20))  # %, MB, packets/sec, etc.

    # Context
    component = Column(String(50))  # alpha, beta, gamma, orchestrator
    hostname = Column(String(100))

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Configuration(Base):
    """Dynamic configuration storage"""
    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(JSON)
    description = Column(String(500))
    category = Column(String(50))  # network, security, ai, etc.

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100))

class DatabaseManager:
    """Database connection and session management"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///./nemesis.db')
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    def init_database(self):
        """Initialize database connection and create tables"""
        if self._initialized:
            return

        try:
            # SQLite-specific configuration for better concurrency
            connect_args = {}
            if self.database_url.startswith('sqlite'):
                connect_args = {
                    'check_same_thread': False,
                }

            self.engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                pool_pre_ping=True,
                echo=False  # Set to True for debugging
            )

            # Create all tables
            Base.metadata.create_all(bind=self.engine)

            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            self._initialized = True
            print(f"Database initialized successfully at {self.database_url}")

        except Exception as e:
            print(f"Failed to initialize database: {e}")
            raise

    def get_session(self) -> Session:
        """Get a database session"""
        if not self._initialized:
            self.init_database()
        return self.SessionLocal()

    def close_session(self, session: Session):
        """Close a database session"""
        if session:
            session.close()

    # Device operations
    def add_or_update_device(self, session: Session, mac_address: str, **kwargs) -> Device:
        """Add or update a device"""
        device = session.query(Device).filter(Device.mac_address == mac_address).first()

        if device:
            # Update existing device
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
        else:
            # Create new device
            device = Device(mac_address=mac_address, **kwargs)
            session.add(device)

        session.commit()
        return device

    def get_device_by_mac(self, session: Session, mac_address: str) -> Optional[Device]:
        """Get device by MAC address"""
        return session.query(Device).filter(Device.mac_address == mac_address).first()

    def get_all_devices(self, session: Session, active_only: bool = True) -> List[Device]:
        """Get all devices"""
        query = session.query(Device)
        if active_only:
            query = query.filter(Device.is_active == True)
        return query.all()

    # Alert operations
    def create_alert(self, session: Session, **kwargs) -> Alert:
        """Create a new alert"""
        alert = Alert(**kwargs)
        session.add(alert)
        session.commit()
        return alert

    def get_recent_alerts(self, session: Session, limit: int = 50) -> List[Alert]:
        """Get recent alerts"""
        return session.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()

    # Traffic logging
    def log_traffic(self, session: Session, device_id: int, **kwargs) -> TrafficLog:
        """Log network traffic"""
        traffic_log = TrafficLog(device_id=device_id, **kwargs)
        session.add(traffic_log)
        session.commit()
        return traffic_log

    # Honeypot interactions
    def log_honeypot_interaction(self, session: Session, **kwargs) -> HoneypotInteraction:
        """Log honeypot interaction"""
        interaction = HoneypotInteraction(**kwargs)
        session.add(interaction)
        session.commit()
        return interaction

    # System metrics
    def record_metric(self, session: Session, **kwargs) -> SystemMetric:
        """Record system metric"""
        metric = SystemMetric(**kwargs)
        session.add(metric)
        session.commit()
        return metric

    # Configuration management
    def get_config(self, session: Session, key: str) -> Any:
        """Get configuration value"""
        config = session.query(Configuration).filter(Configuration.key == key).first()
        return config.value if config else None

    def set_config(self, session: Session, key: str, value: Any, description: str = "", category: str = "general") -> Configuration:
        """Set configuration value"""
        config = session.query(Configuration).filter(Configuration.key == key).first()

        if config:
            config.value = value
            config.description = description
            config.category = category
        else:
            config = Configuration(key=key, value=value, description=description, category=category)
            session.add(config)

        session.commit()
        return config

    # Cleanup operations
    def cleanup_old_data(self, session: Session, days: int = 30):
        """Clean up old data"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Clean up old traffic logs
        session.query(TrafficLog).filter(TrafficLog.timestamp < cutoff_date).delete()

        # Clean up old honeypot interactions
        session.query(HoneypotInteraction).filter(HoneypotInteraction.timestamp < cutoff_date).delete()

        # Clean up old system metrics
        session.query(SystemMetric).filter(SystemMetric.timestamp < cutoff_date).delete()

        session.commit()

# Global database instance
db_manager = DatabaseManager()

def get_db_session() -> Session:
    """Get a database session (use in FastAPI dependencies)"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        db_manager.close_session(session)