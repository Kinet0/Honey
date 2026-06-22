"""
Application configuration and settings
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/honeypot_dashboard"
    
    # API Configuration
    API_TITLE: str = "Honeypot Dashboard API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # seconds
    MAX_WEBSOCKET_CONNECTIONS: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Features
    DEBUG: bool = False
    ENABLE_DEMO_MODE: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # GeoIP Configuration
    MAXMIND_LICENSE_KEY: str = ""  # Set if using GeoIP2
    USE_GEOIP: bool = False
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
