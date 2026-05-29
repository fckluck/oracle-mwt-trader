"""
Backend Configuration

Settings from environment or .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Oracle MWT Trader"
    phase: str = "observe_only"
    live_execution: bool = False
    
    # Server
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite:///oracle_mwt.db"
    
    # Conviction
    conviction_threshold: float = 0.75
    window_minutes: int = 15
    min_cluster_size: int = 2
    
    # Paper Trading
    starting_balance: float = 100000.0
    daily_profit_cap: float = 10000.0
    
    # Assets (Phase 1 only)
    active_assets: str = "SOL,BTC,ETH,HYPE"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_active_assets(self) -> List[str]:
        """Parse active assets"""
        return [a.strip().upper() for a in self.active_assets.split(",")]


settings = Settings()
