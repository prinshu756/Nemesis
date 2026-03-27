"""
Nemesis Configuration Management
Environment-based configuration with .env support
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Database
    database_url: str = Field(default="sqlite:///./nemesis.db", env="DATABASE_URL")

    # Network
    network_interface: str = Field(default="eth0", env="NETWORK_INTERFACE")
    packet_capture_enabled: bool = Field(default=True, env="PACKET_CAPTURE_ENABLED")
    scan_interval: int = Field(default=30, env="SCAN_INTERVAL")
    max_devices: int = Field(default=1000, env="MAX_DEVICES")

    # AI/ML
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    use_local_ai: bool = Field(default=False, env="USE_LOCAL_AI")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_db_enabled: bool = Field(default=True, env="VECTOR_DB_ENABLED")

    # Security
    secret_key: str = Field(default="your-secret-key-here-change-in-production", env="SECRET_KEY")
    jwt_secret: str = Field(default="your-jwt-secret-here", env="JWT_SECRET")
    encryption_key: str = Field(default="your-32-char-encryption-key-here", env="ENCRYPTION_KEY")

    # Docker/Honeypot
    docker_enabled: bool = Field(default=True, env="DOCKER_ENABLED")
    honeypot_auto_deploy: bool = Field(default=True, env="HONEYPOT_AUTO_DEPLOY")
    honeypot_images: str = Field(default="cowrie/cowrie:latest,opencanary/opencanary:latest", env="HONEYPOT_IMAGES")
    honeypot_port_range: str = Field(default="22000-22999", env="HONEYPOT_PORT_RANGE")

    # eBPF
    ebpf_enabled: bool = Field(default=True, env="EBPF_ENABLED")
    ebpf_mount_point: str = Field(default="/sys/fs/bpf", env="EBPF_MOUNT_POINT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/nemesis.log", env="LOG_FILE")
    log_max_size: int = Field(default=10485760, env="LOG_MAX_SIZE")  # 10MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8001, env="API_PORT")
    cors_origins: str = Field(default="http://localhost:5174,http://localhost:3000", env="CORS_ORIGINS")
    websocket_enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")

    # Monitoring
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    alert_retention_days: int = Field(default=30, env="ALERT_RETENTION_DAYS")
    traffic_monitoring_enabled: bool = Field(default=True, env="TRAFFIC_MONITORING_ENABLED")

    # External APIs
    virustotal_api_key: Optional[str] = Field(default=None, env="VIRUSTOTAL_API_KEY")
    shodan_api_key: Optional[str] = Field(default=None, env="SHODAN_API_KEY")
    abuseipdb_api_key: Optional[str] = Field(default=None, env="ABUSEIPDB_API_KEY")
    ipinfo_api_key: Optional[str] = Field(default=None, env="IPINFO_API_KEY")

    # Notifications
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    discord_webhook_url: Optional[str] = Field(default=None, env="DISCORD_WEBHOOK_URL")
    email_smtp_server: Optional[str] = Field(default=None, env="EMAIL_SMTP_SERVER")
    email_smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")
    email_username: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    email_password: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    email_from: Optional[str] = Field(default=None, env="EMAIL_FROM")

    # Advanced Features
    graph_database_enabled: bool = Field(default=False, env="GRAPH_DATABASE_ENABLED")
    graph_db_url: str = Field(default="neo4j://localhost:7687", env="GRAPH_DB_URL")
    graph_db_user: str = Field(default="neo4j", env="GRAPH_DB_USER")
    graph_db_password: str = Field(default="password", env="GRAPH_DB_PASSWORD")

    redis_enabled: bool = Field(default=False, env="REDIS_ENABLED")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Development
    debug: bool = Field(default=True, env="DEBUG")
    development: bool = Field(default=True, env="DEVELOPMENT")
    auto_reload: bool = Field(default=True, env="AUTO_RELOAD")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Legacy config dictionary for backward compatibility
config = {
    # Network
    'network.interface': settings.network_interface,
    'network.scan_interval': settings.scan_interval,
    'packet_capture.enabled': settings.packet_capture_enabled,

    # AI
    'ai.use_local_ai': settings.use_local_ai,
    'ai.ollama_url': settings.ollama_url,
    'ai.model': settings.ollama_model,
    'ai.embedding_model': settings.embedding_model,

    # Docker/Honeypot
    'honeypot.auto_deploy': settings.honeypot_auto_deploy,
    'honeypot.images': settings.honeypot_images.split(','),
    'docker.enabled': settings.docker_enabled,

    # eBPF
    'ebpf.enabled': settings.ebpf_enabled,
    'ebpf.mount_point': settings.ebpf_mount_point,

    # API
    'api.host': settings.api_host,
    'api.port': settings.api_port,
    'websocket.enabled': settings.websocket_enabled,

    # Logging
    'logging.level': settings.log_level,
    'logging.file': settings.log_file,

    # Security
    'security.secret_key': settings.secret_key,
    'security.encryption_key': settings.encryption_key,

    # Monitoring
    'monitoring.enabled': settings.metrics_enabled,
    'monitoring.interval': settings.health_check_interval,
}

def get_cors_origins() -> list:
    """Get CORS origins as a list"""
    return [origin.strip() for origin in settings.cors_origins.split(',')]

def get_honeypot_images() -> list:
    """Get honeypot images as a list"""
    return [image.strip() for image in settings.honeypot_images.split(',')]

def get_honeypot_port_range() -> tuple:
    """Get honeypot port range as tuple (start, end)"""
    try:
        start, end = settings.honeypot_port_range.split('-')
        return int(start), int(end)
    except (ValueError, AttributeError):
        return 22000, 22999

def is_production() -> bool:
    """Check if running in production mode"""
    return not settings.development

def get_database_url() -> str:
    """Get database URL with environment variable override"""
    return os.getenv('DATABASE_URL', settings.database_url)

def save_config_to_env():
    """Save current settings to .env file"""
    env_path = Path('.env')

    # Read existing .env if it exists
    existing_config = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    existing_config[key] = value

    # Update with current settings
    current_config = {}
    for field_name, field in Settings.__fields__.items():
        env_name = field.field_info.extra.get('env', field_name.upper())
        value = getattr(settings, field_name)

        # Convert to string
        if isinstance(value, bool):
            value = str(value).lower()
        elif isinstance(value, list):
            value = ','.join(str(v) for v in value)
        else:
            value = str(value)

        current_config[env_name] = value

    # Merge and write
    final_config = {**existing_config, **current_config}

    with open(env_path, 'w') as f:
        f.write("# Nemesis SOC Configuration\n")
        f.write("# Auto-generated from settings\n\n")

        for key, value in sorted(final_config.items()):
            f.write(f"{key}={value}\n")

    print(f"Configuration saved to {env_path}")

# Initialize database and create tables on import
from .database import db_manager