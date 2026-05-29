"""
Market Bias Analysis (Stub)

Placeholder for directional bias detection.
"""

from enum import Enum
from pydantic import BaseModel
from typing import Optional


class BiasDirection(str, Enum):
    """Market bias direction"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class BiasState(BaseModel):
    """Market bias state"""
    
    asset: str
    direction: BiasDirection = BiasDirection.NEUTRAL
    confidence: float = 0.5
    volatility_state: str = "normal"
    notes: str = "Stub - no live data"


def get_btc_eth_bias_stub() -> dict:
    """Get stub bias for BTC and ETH
    
    Phase 1: Returns neutral placeholders
    """
    return {
        "BTC": BiasState(asset="BTC", direction=BiasDirection.NEUTRAL),
        "ETH": BiasState(asset="ETH", direction=BiasDirection.NEUTRAL),
    }
