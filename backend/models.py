"""
Data models for Oracle MWT Trader
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TradeDirection(str, Enum):
    """Trade direction enum"""
    LONG = "long"
    SHORT = "short"


class TradeVenue(str, Enum):
    """Supported trading venues"""
    DYDX = "dydx"
    DRIFT = "drift"
    MARINADE = "marinade"
    PHANTOM = "phantom"


class WalletEvent(BaseModel):
    """Normalized wallet event"""
    
    event_id: str
    venue: str
    wallet_address: str
    asset: str
    direction: str
    size: float
    entry_price: float
    timestamp: datetime
    tx_hash: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt-123",
                "venue": "drift",
                "wallet_address": "0xabc123...",
                "asset": "SOL",
                "direction": "long",
                "size": 10.5,
                "entry_price": 140.50,
                "timestamp": "2026-05-28T15:30:00Z",
                "tx_hash": "0xdef456...",
            }
        }


class MWTObject(BaseModel):
    """Multi-Wallet Tracking normalized object"""
    
    mwt_id: str
    asset: str
    direction: str
    conviction_score: float = Field(ge=0.0, le=1.0)
    wallet_count: int
    avg_size: float
    venue_distribution: Dict[str, int] = Field(default_factory=dict)
    cluster_start: datetime
    cluster_end: datetime
    event_count: int = 0


class ConvictionSignal(BaseModel):
    """Current conviction signal"""
    
    timestamp: datetime
    asset: str
    direction: str
    conviction_score: float = Field(ge=0.0, le=1.0)
    wallet_count: int
    confidence: float = Field(ge=0.0, le=1.0)
    cluster_count: int
    supporting_events: int


class HealthResponse(BaseModel):
    """Server health check response"""
    
    status: str = "healthy"
    version: str
    timestamp: datetime
    uptime_seconds: float


class IngestEventRequest(BaseModel):
    """Request to ingest a wallet event"""
    
    venue: str
    wallet_address: str
    asset: str
    direction: str
    size: float
    entry_price: float
    timestamp: datetime
    tx_hash: str
    metadata: Optional[Dict[str, Any]] = None


class IngestEventResponse(BaseModel):
    """Response from event ingestion"""
    
    event_id: str
    mwt_id: Optional[str] = None
    conviction_score: Optional[float] = None
    timestamp: datetime
    status: str = "ingested"


class RegisterWalletRequest(BaseModel):
    """Request to register a wallet"""
    
    wallet_address: str
    venue: str
    nickname: Optional[str] = None


class RegisterWalletResponse(BaseModel):
    """Response for wallet registration"""
    
    wallet_id: str
    wallet_address: str
    venue: str
    registered_at: datetime
    status: str = "active"


class SeedResponse(BaseModel):
    """Response from seed operation"""
    
    status: str
    events_created: int
    wallets_registered: int
    timestamp: datetime
