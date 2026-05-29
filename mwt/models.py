"""
MWT Data Models

Pydantic models for wallet tracking, profiles, and signals.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class Asset(str, Enum):
    """Supported assets (Phase 1 only)"""
    SOL = "SOL"
    BTC = "BTC"
    ETH = "ETH"
    HYPE = "HYPE"


class Side(str, Enum):
    """Trade direction"""
    LONG = "long"
    SHORT = "short"


class WalletClass(str, Enum):
    """Wallet classification based on performance"""
    WHALE = "whale"
    ACTIVE_TRADER = "active_trader"
    UNKNOWN = "unknown"


class Platform(str, Enum):
    """Supported platforms"""
    HYPERLIQUID = "hyperliquid"
    JUPITER = "jupiter"
    OSTIUM = "ostium"
    APEX = "apex"
    UNKNOWN = "unknown"


class MWTTrade(BaseModel):
    """Multi-Wallet Tracking Trade
    
    Normalized wallet trading activity from any platform.
    """
    
    wallet_id: str = Field(..., description="Unique wallet identifier")
    wallet_class: WalletClass = Field(default=WalletClass.UNKNOWN)
    asset: Asset = Field(..., description="Asset being traded")
    side: Side = Field(..., description="Trade direction (long/short)")
    leverage: float = Field(gt=0, le=200, description="Trade leverage")
    size_usd: float = Field(gt=0, description="Position size in USD")
    entry_price: float = Field(gt=0, description="Entry price")
    platform: Platform = Field(..., description="Trading platform")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw: Dict[str, Any] = Field(default_factory=dict, description="Raw platform data")
    
    class Config:
        use_enum_values = True


class WalletProfile(BaseModel):
    """Wallet Performance Profile
    
    Metadata about wallet trading performance and classification.
    """
    
    wallet_id: str
    winrate: float = Field(ge=0, le=1, default=0.5)
    avg_rr: float = Field(ge=0, default=1.0, description="Average risk-reward ratio")
    consistency: float = Field(ge=0, le=1, default=0.5, description="Trade consistency")
    wallet_class: WalletClass = Field(default=WalletClass.UNKNOWN)
    trades_count: int = Field(ge=0, default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class ConvictionSignal(BaseModel):
    """MWT Conviction Signal
    
    Aggregated smart money activity indicating directional conviction.
    """
    
    asset: Asset
    direction: Side
    total_size_usd: float = Field(gt=0, description="Total position size")
    avg_entry: float = Field(gt=0, description="Weighted average entry price")
    wallet_count: int = Field(gt=0, description="Number of coordinated wallets")
    platforms: List[str] = Field(default_factory=list, description="Platforms involved")
    conviction_score: float = Field(ge=0, le=1, description="Signal strength (0-1)")
    first_seen: datetime
    last_seen: datetime
    trades: List[MWTTrade] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
