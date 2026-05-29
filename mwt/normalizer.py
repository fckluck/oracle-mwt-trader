"""
MWT Normalizer

Converts raw platform data into normalized MWTTrade objects.
"""

from mwt.models import MWTTrade, Asset, Side, Platform, WalletClass
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Allowed assets for Phase 1
ALLOWED_ASSETS = {Asset.SOL, Asset.BTC, Asset.ETH, Asset.HYPE}


def normalize_raw_trade(raw: Dict[str, Any], wallet_id: str = None) -> MWTTrade:
    """Normalize raw trade data into MWTTrade
    
    Args:
        raw: Raw trade data dict
        wallet_id: Override wallet ID if provided
        
    Returns:
        Normalized MWTTrade
        
    Raises:
        ValueError: If data is invalid
    """
    try:
        # Extract required fields
        wallet_id = wallet_id or raw.get("wallet_id", "")
        if not wallet_id:
            raise ValueError("wallet_id required")
        
        # Asset validation
        asset_str = raw.get("asset", "").upper()
        try:
            asset = Asset[asset_str]
        except KeyError:
            raise ValueError(f"Asset {asset_str} not supported. Allowed: {list(ALLOWED_ASSETS)}")
        
        if asset not in ALLOWED_ASSETS:
            raise ValueError(f"Asset {asset} not in Phase 1 active assets")
        
        # Side validation
        side_str = raw.get("side", "").lower()
        if side_str not in ["long", "short"]:
            raise ValueError(f"Side must be 'long' or 'short', got {side_str}")
        side = Side.LONG if side_str == "long" else Side.SHORT
        
        # Leverage validation
        leverage = float(raw.get("leverage", 1.0))
        if leverage <= 0 or leverage > 200:
            raise ValueError(f"Leverage must be > 0 and <= 200, got {leverage}")
        
        # Size validation
        size_usd = float(raw.get("size_usd", 0))
        if size_usd <= 0:
            raise ValueError(f"Size must be > 0, got {size_usd}")
        
        # Price validation
        entry_price = float(raw.get("entry_price", 0))
        if entry_price <= 0:
            raise ValueError(f"Entry price must be > 0, got {entry_price}")
        
        # Platform normalization
        platform_str = raw.get("platform", "unknown").lower()
        try:
            platform = Platform[platform_str.upper()]
        except KeyError:
            platform = Platform.UNKNOWN
        
        # Timestamp
        timestamp_str = raw.get("timestamp")
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        elif isinstance(timestamp_str, datetime):
            timestamp = timestamp_str
        else:
            timestamp = datetime.utcnow()
        
        # Create trade
        trade = MWTTrade(
            wallet_id=wallet_id,
            wallet_class=WalletClass(raw.get("wallet_class", "unknown")),
            asset=asset,
            side=side,
            leverage=leverage,
            size_usd=size_usd,
            entry_price=entry_price,
            platform=platform,
            timestamp=timestamp,
            raw=raw,
        )
        
        logger.info(f"✅ Normalized {asset} {side} trade from {wallet_id}")
        return trade
        
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"❌ Normalization failed: {e}")
        raise ValueError(f"Invalid trade data: {str(e)}")


def validate_asset(asset_str: str) -> Asset:
    """Validate asset string
    
    Args:
        asset_str: Asset string
        
    Returns:
        Asset enum value
        
    Raises:
        ValueError: If asset not supported
    """
    asset_upper = asset_str.upper()
    try:
        asset = Asset[asset_upper]
        if asset not in ALLOWED_ASSETS:
            raise ValueError(f"Asset {asset} not in Phase 1 active set")
        return asset
    except KeyError:
        raise ValueError(f"Unsupported asset {asset_str}")
