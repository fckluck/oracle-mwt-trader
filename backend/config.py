"""
Configuration management for Oracle MWT Trader
"""

from pydantic_settings import BaseSettings
from typing import List
from enum import Enum


class StorageType(str, Enum):
    """Storage backend types"""
    MEMORY = "memory"
    SQLITE = "sqlite"


class Settings(BaseSettings):
    """Application settings from environment"""
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    log_level: str = "INFO"
    
    # Storage
    storage_type: StorageType = StorageType.MEMORY
    database_url: str = "sqlite:///./oracle_mwt.db"
    
    # Conviction Engine
    conviction_window_minutes: int = 60
    min_cluster_size: int = 2
    conviction_threshold: float = 0.65
    
    # Assets (Phase 1)
    active_assets: List[str] = ["SOL", "BTC", "ETH", "HYPE"]
    
    # Mock Data
    use_mock_data: bool = True
    mock_events_per_minute: int = 5
    
    # API Config
    api_version: str = "v1"
    enable_docs: bool = True
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
