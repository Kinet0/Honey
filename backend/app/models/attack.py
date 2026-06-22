"""
Database models for attack data
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Float, ForeignKey,
    TIMESTAMP, Enum as SQLEnum, Text, JSON, BigInteger, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class EventType(str, Enum):
    """Attack event types"""
    CONNECTION = "connection"
    AUTH_ATTEMPT = "auth_attempt"
    LOGIN = "login"
    COMMAND = "command"
    DOWNLOAD = "download"


class Severity(str, Enum):
    """Event severity levels"""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"


class CommandClassification(str, Enum):
    """Command classification types"""
    RECONNAISSANCE = "reconnaissance"
    FILE_DOWNLOAD = "file_download"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    NETWORKING = "networking"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class ThreatLevel(str, Enum):
    """Attacker threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Attacker(Base):
    """Attacker profile"""
    __tablename__ = "attackers"

    ip_address = Column(String(45), primary_key=True, index=True)
    country_code = Column(String(2), nullable=False)
    asn = Column(Integer, nullable=True, index=True)
    isp = Column(String(255), nullable=True)
    first_seen = Column(TIMESTAMP(timezone=True), nullable=False)
    last_seen = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    total_sessions = Column(Integer, default=0)
    total_commands = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    max_severity = Column(SQLEnum(Severity), default=Severity.INFO)
    threat_level = Column(SQLEnum(ThreatLevel), default=ThreatLevel.LOW, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="attacker", cascade="all, delete-orphan")
    attacks = relationship("Attack", back_populates="attacker", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_attackers_last_seen', 'last_seen', postgresql_using='btree'),
        Index('idx_attackers_country_code', 'country_code'),
        Index('idx_attackers_threat_level', 'threat_level'),
    )


class Session(Base):
    """Attack session"""
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)
    attacker_ip = Column(String(45), ForeignKey("attackers.ip_address"), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    total_commands = Column(Integer, default=0)
    protocol = Column(String(10), default="ssh")
    honeypot_version = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attacker = relationship("Attacker", back_populates="sessions")
    attacks = relationship("Attack", back_populates="session", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="session", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="session", cascade="all, delete-orphan")
    credentials = relationship("Credential", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_sessions_attacker_ip', 'attacker_ip'),
        Index('idx_sessions_start_time', 'start_time', postgresql_using='btree', postgresql_order='DESC'),
        Index('idx_sessions_status', 'status'),
    )


class Attack(Base):
    """Attack event"""
    __tablename__ = "attacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    session_id = Column(String(255), ForeignKey("sessions.id"), nullable=True)
    attacker_ip = Column(String(45), ForeignKey("attackers.ip_address"), nullable=False)
    event_type = Column(SQLEnum(EventType), nullable=False)
    severity = Column(SQLEnum(Severity), default=Severity.INFO)
    country_code = Column(String(2), nullable=True, index=True)
    asn = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="attacks")
    attacker = relationship("Attacker", back_populates="attacks")

    __table_args__ = (
        Index('idx_attacks_timestamp', 'timestamp', postgresql_using='btree', postgresql_order='DESC'),
        Index('idx_attacks_session_id', 'session_id'),
        Index('idx_attacks_attacker_ip', 'attacker_ip'),
        Index('idx_attacks_severity', 'severity'),
        Index('idx_attacks_country_code', 'country_code'),
    )


class Command(Base):
    """Executed command"""
    __tablename__ = "commands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    command = Column(Text, nullable=False)
    classification = Column(SQLEnum(CommandClassification), nullable=True)
    success = Column(Boolean, default=True)
    output = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="commands")

    __table_args__ = (
        Index('idx_commands_session_id', 'session_id'),
        Index('idx_commands_timestamp', 'timestamp', postgresql_using='btree', postgresql_order='DESC'),
        Index('idx_commands_classification', 'classification'),
    )


class Download(Base):
    """Payload download"""
    __tablename__ = "downloads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    file_hash = Column(String(64), nullable=True)
    file_size = Column(Integer, nullable=True)
    url = Column(String(1024), nullable=True)
    file_type = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="downloads")

    __table_args__ = (
        Index('idx_downloads_session_id', 'session_id'),
        Index('idx_downloads_timestamp', 'timestamp', postgresql_using='btree', postgresql_order='DESC'),
    )


class Credential(Base):
    """Captured credentials"""
    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("sessions.id"), nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    username = Column(String(255), nullable=False, index=True)
    password = Column(String(255), nullable=False)
    success = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=1)
    last_used = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="credentials")

    __table_args__ = (
        Index('idx_credentials_username', 'username'),
        Index('idx_credentials_timestamp', 'timestamp', postgresql_using='btree', postgresql_order='DESC'),
    )


class ASNLookup(Base):
    """Cached ASN/ISP information"""
    __tablename__ = "asn_lookups"

    asn = Column(Integer, primary_key=True)
    isp = Column(String(255), nullable=True)
    country_code = Column(String(2), nullable=True)
    last_updated = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    lookup_count = Column(Integer, default=0)


class ActivityStats(Base):
    """Pre-calculated activity statistics"""
    __tablename__ = "activity_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False)
    hour = Column(Integer, nullable=True)  # 0-23 for hourly stats
    attack_count = Column(Integer, default=0)
    unique_attackers = Column(Integer, default=0)
    unique_countries = Column(Integer, default=0)
    total_commands = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index('idx_activity_stats_date', 'date', postgresql_using='btree', postgresql_order='DESC'),
        Index('idx_activity_stats_hour', 'date', 'hour'),
    )
