"""
Configuration settings for Security Monitoring Agent System
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000  # Railway will override with $PORT env variable
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*"  # Comma-separated list or "*" for all

    # AI Configuration
    AI_PROVIDER: str = "openai"  # "openai" or "gemini"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AI_MODEL: str = "gpt-3.5-turbo"  # Default to accessible OpenAI model
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000

    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "security_monitoring"

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Network Monitoring
    NETWORK_INTERFACE: str = "eth0"
    CAPTURE_TIMEOUT: int = 60
    MAX_PACKETS_PER_BATCH: int = 1000

    # Attack Simulation
    ENABLE_ATTACK_SIM: bool = True
    MAX_SIMULATION_DURATION: int = 300
    ALLOWED_TARGET_NETWORKS: str = "192.168.1.0/24,10.0.0.0/24"

    # Threat Intelligence
    THREAT_DB_UPDATE_INTERVAL: int = 3600
    CVE_API_ENABLED: bool = True

    # Notifications
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    DISCORD_WEBHOOK_URL: str = ""
    EMAIL_ENABLED: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/smas.log"
    LOG_ROTATION: str = "100 MB"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_networks(self) -> List[str]:
        """Parse allowed target networks"""
        return [net.strip() for net in self.ALLOWED_TARGET_NETWORKS.split(",")]

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Global settings instance
settings = Settings()
