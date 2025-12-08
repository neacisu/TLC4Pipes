"""
TLC4Pipe Configuration
Pydantic Settings for environment-based configuration
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://tlc4pipe:tlc4pipe@localhost:5432/tlc4pipe"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:80"
    
    # Pipe Loading Configuration
    DEFAULT_PIPE_LENGTH_M: float = 12.0
    MAX_TRUCK_PAYLOAD_KG: int = 24000
    MIN_GAP_CLEARANCE_MM: float = 15.0
    GAP_DIAMETER_FACTOR: float = 0.015
    MAX_NESTING_LEVELS: int = 4
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
