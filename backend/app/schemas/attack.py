"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field


class EventTypeEnum(str, Enum):
    """Event type enumeration"""
    CONNECTION = "connection"
    AUTH_ATTEMPT = "auth_attempt"
    LOGIN = "login"
    COMMAND = "command"
    DOWNLOAD = "download"


class SeverityEnum(str, Enum):
    """Severity level enumeration"""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommandClassificationEnum(str, Enum):
    """Command classification enumeration"""
    RECONNAISSANCE = "reconnaissance"
    FILE_DOWNLOAD = "file_download"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    NETWORKING = "networking"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class ThreatLevelEnum(str, Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Attacker Schemas
class AttackerBase(BaseModel):
    """Base attacker schema"""
    country_code: str
    asn: Optional[int] = None
    isp: Optional[str] = None


class AttackerCreate(AttackerBase):
    """Attacker creation schema"""
    ip_address: str
    first_seen: datetime
    last_seen: datetime


class AttackerResponse(AttackerBase):
    """Attacker response schema"""
    ip_address: str
    first_seen: datetime
    last_seen: datetime
    total_sessions: int
    total_commands: int
    total_downloads: int
    max_severity: SeverityEnum
    threat_level: ThreatLevelEnum

    class Config:
        from_attributes = True


# Session Schemas
class SessionBase(BaseModel):
    """Base session schema"""
    status: str = "active"
    protocol: str = "ssh"


class SessionCreate(SessionBase):
    """Session creation schema"""
    id: str
    attacker_ip: str
    start_time: datetime


class SessionResponse(SessionBase):
    """Session response schema"""
    id: str
    attacker_ip: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_commands: int

    class Config:
        from_attributes = True


# Command Schemas
class CommandBase(BaseModel):
    """Base command schema"""
    command: str
    classification: Optional[CommandClassificationEnum] = None
    success: bool = True


class CommandCreate(CommandBase):
    """Command creation schema"""
    session_id: str
    timestamp: datetime
    output: Optional[str] = None


class CommandResponse(CommandCreate):
    """Command response schema"""
    id: str

    class Config:
        from_attributes = True


# Attack Schemas
class AttackBase(BaseModel):
    """Base attack schema"""
    event_type: EventTypeEnum
    severity: SeverityEnum = SeverityEnum.INFO
    country_code: Optional[str] = None
    asn: Optional[int] = None


class AttackCreate(AttackBase):
    """Attack creation schema"""
    timestamp: datetime
    session_id: Optional[str] = None
    attacker_ip: str
    metadata: Optional[dict] = None


class AttackResponse(AttackBase):
    """Attack response schema"""
    id: str
    timestamp: datetime
    session_id: Optional[str] = None
    attacker_ip: str
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


# Download Schemas
class DownloadBase(BaseModel):
    """Base download schema"""
    filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None


class DownloadCreate(DownloadBase):
    """Download creation schema"""
    session_id: str
    timestamp: datetime
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    url: Optional[str] = None


class DownloadResponse(DownloadCreate):
    """Download response schema"""
    id: str

    class Config:
        from_attributes = True


# Credential Schemas
class CredentialBase(BaseModel):
    """Base credential schema"""
    username: str
    password: str


class CredentialCreate(CredentialBase):
    """Credential creation schema"""
    session_id: Optional[str] = None
    timestamp: datetime
    success: bool = False


class CredentialResponse(CredentialCreate):
    """Credential response schema"""
    id: str

    class Config:
        from_attributes = True


# Statistics Schemas
class AttackStatistics(BaseModel):
    """Attack statistics"""
    attacks_today: int
    attacks_this_week: int
    attacks_this_month: int
    unique_attackers: int
    unique_countries: int
    total_commands: int
    total_downloads: int
    avg_session_duration: Optional[float] = None


# Search/Filter Schemas
class AttackFilter(BaseModel):
    """Attack filter parameters"""
    country: Optional[str] = None
    asn: Optional[int] = None
    username: Optional[str] = None
    command: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# List Response Schemas
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[Any]
    total: int
    limit: int
    offset: int


class SearchResponse(PaginatedResponse):
    """Search response with filters applied"""
    filters_applied: Optional[dict] = None


# Top Items Schemas
class TopItem(BaseModel):
    """Generic top item"""
    rank: int
    name: str
    value: int
    percentage: float


class TopList(BaseModel):
    """Top list response"""
    type: str
    data: List[TopItem]


# Analytics Schemas
class TrendData(BaseModel):
    """Trend data point"""
    timestamp: datetime
    attacks: int
    unique_attackers: int
    unique_countries: int


class TrendResponse(BaseModel):
    """Trend response"""
    period: str
    data: List[TrendData]


class MapData(BaseModel):
    """Geographic data point"""
    country_code: str
    country_name: str
    latitude: float
    longitude: float
    attack_count: int
    unique_attackers: int
    intensity: float


class MapResponse(BaseModel):
    """Map response"""
    data: List[MapData]


# WebSocket Schemas
class WebSocketMessage(BaseModel):
    """WebSocket message"""
    type: str
    data: Optional[dict] = None
    filters: Optional[dict] = None


class WebSocketEvent(BaseModel):
    """WebSocket event"""
    type: str
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)
