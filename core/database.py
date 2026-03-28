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
import json

Base = declarative_base()

# Association tables for many-to-many relationships
device_vulnerabilities = Table(
    'device_vulnerabilities',
    Base.metadata,
    Column('device_id', Integer, ForeignKey('devices.id')),
    Column('vulnerability_id', Integer, ForeignKey('vulnerabilities.id'))
)

device_alerts = Table(
    'device_alerts',
    Base.metadata,
    Column('device_id', Integer, ForeignKey('devices.id')),
    Column('alert_id', Integer, ForeignKey('alerts.id'))
)


class Device(Base):
    """Network device information"""
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    mac_address = Column(String(17), unique=True, index=True)
    ip_address = Column(String(45))
    hostname = Column(String(255))
    device_type = Column(String(50))
    os_fingerprint = Column(String(255))
    vendor = Column(String(255))
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default='low')
    threat_level = Column(String(20), default='low')
    
    # Behavioral analysis
    packet_count = Column(Integer, default=0)
    bytes_transferred = Column(Integer, default=0)
    connection_count = Column(Integer, default=0)
    port_scan_detected = Column(Boolean, default=False)
    anomalous_behavior = Column(JSON)

    # Device state
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    isolation_status = Column(String(20), default='normal')
    
    # Network properties
    ports = Column(JSON, default={})
    services = Column(JSON, default={})

    # Database metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    severity = Column(String(20))
    cvss_score = Column(Float)
    affected_products = Column(JSON)
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
    severity = Column(String(20), default='medium')
    alert_type = Column(String(50))
    source = Column(String(50))

    # Alert data
    level = Column(String(20), default='info')
    message = Column(Text)
    device_mac = Column(String(17))
    risk_score = Column(Float)
    details = Column(JSON)

    # Status and response
    status = Column(String(20), default='new')
    assigned_to = Column(String(100))
    response_actions = Column(JSON)
    resolution_notes = Column(Text)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
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
    source_ip = Column(String(45))
    destination_ip = Column(String(45))
    src_ip = Column(String(45))
    dst_ip = Column(String(45))
    source_port = Column(Integer)
    destination_port = Column(Integer)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String(10))

    # Traffic metrics
    packet_size = Column(Integer)
    packet_count = Column(Integer, default=1)
    bytes_transferred = Column(Integer)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration = Column(Float)

    # Classification
    traffic_type = Column(String(50))
    classification_reason = Column(String(200))
    flags = Column(String(50))

    # Additional data
    details = Column(JSON)

    # Relationships
    device = relationship("Device", back_populates="traffic_logs")


class HoneypotInteraction(Base):
    """Honeypot detection events"""
    __tablename__ = 'honeypot_interactions'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'), index=True)
    honeypot_id = Column(String(100), index=True)
    honeypot_type = Column(String(50))

    # Interaction details
    ip_address = Column(String(45))
    src_ip = Column(String(45))
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String(10))
    threat_type = Column(String(100))

    # Attack information
    attack_type = Column(String(100))
    payload = Column(Text)
    credentials_used = Column(JSON)

    # Response
    response_sent = Column(Text)
    session_log = Column(Text)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(20), default='medium')
    blocked = Column(Boolean, default=True)
    event_type = Column(String(50), default='detection')
    container_id = Column(String(100))
    interaction_type = Column(String(50), default='detected')

    # Additional data
    details = Column(JSON)

    # Relationships
    device = relationship("Device", back_populates="honeypot_interactions")


class SystemMetric(Base):
    """System performance and health metrics"""
    __tablename__ = 'system_metrics'

    id = Column(Integer, primary_key=True)
    metric_type = Column(String(50), index=True)
    metric_name = Column(String(100))
    value = Column(Float)
    unit = Column(String(20))

    # Context
    component = Column(String(50))
    hostname = Column(String(100))

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON)


class Configuration(Base):
    """Dynamic configuration storage"""
    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(JSON)
    description = Column(String(500))
    category = Column(String(50))

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
                echo=False
            )

            # Create all tables
            Base.metadata.create_all(bind=self.engine)

            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            self._initialized = True
            print(f"✓ Database initialized at {self.database_url}")

        except Exception as e:
            print(f"✗ Failed to initialize database: {e}")
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
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
        else:
            device = Device(mac_address=mac_address, **kwargs)
            session.add(device)

        session.commit()
        return device

    def get_device_by_mac(self, session: Session, mac_address: str) -> Optional[Device]:
        """Get device by MAC address"""
        return session.query(Device).filter(Device.mac_address == mac_address).first()

    # Alert operations
    def add_alert(self, session: Session, **kwargs) -> Alert:
        """Add an alert"""
        alert = Alert(**kwargs)
        session.add(alert)
        session.commit()
        return alert

    # Traffic log operations
    def add_traffic_log(self, session: Session, **kwargs) -> TrafficLog:
        """Add a traffic log entry"""
        log = TrafficLog(**kwargs)
        session.add(log)
        session.commit()
        return log

    # Honeypot operations
    def add_honeypot_interaction(self, session: Session, **kwargs) -> HoneypotInteraction:
        """Add a honeypot interaction"""
        interaction = HoneypotInteraction(**kwargs)
        session.add(interaction)
        session.commit()
        return interaction

    # System metrics
    def add_system_metric(self, session: Session, **kwargs) -> SystemMetric:
        """Add a system metric"""
        metric = SystemMetric(**kwargs)
        session.add(metric)
        session.commit()
        return metric

    # Cleanup operations
    def cleanup_old_data(self, session: Session, days: int = 30):
        """Clean up old data"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        try:
            # Clean old traffic logs
            old_traffic = session.query(TrafficLog).filter(TrafficLog.timestamp < cutoff_date).delete()
            
            # Clean old system metrics
            old_metrics = session.query(SystemMetric).filter(SystemMetric.timestamp < cutoff_date).delete()
            
            # Clean old alerts
            old_alerts = session.query(Alert).filter(Alert.timestamp < cutoff_date).delete()
            
            session.commit()
            print(f"Cleaned up: {old_traffic} traffic logs, {old_metrics} metrics, {old_alerts} alerts")

        except Exception as e:
            session.rollback()
            print(f"Error during cleanup: {e}")
            raise


# Global database instance
db_manager = DatabaseManager()


def get_db_session() -> Session:
    """Get a database session (use in FastAPI dependencies)"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        db_manager.close_session(session)
