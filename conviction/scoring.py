"""
Conviction Scoring Functions

Computes weight factors for trades based on wallet profile and market conditions.
"""

from mwt.models import WalletProfile, MWTTrade
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger(__name__)


def wallet_score(profile: WalletProfile) -> float:
    """Score wallet profile (0-1)
    
    Formula: score = winrate*0.5 + avg_rr_normalized*0.3 + consistency*0.2
    
    Args:
        profile: WalletProfile to score
        
    Returns:
        Score 0-1, clamped
    """
    # Normalize avg_rr to 0-1 range (assume max 5.0 RR)
    rr_normalized = min(profile.avg_rr / 5.0, 1.0)
    
    score = (
        profile.winrate * 0.5 +
        rr_normalized * 0.3 +
        profile.consistency * 0.2
    )
    
    return min(max(score, 0.0), 1.0)


def leverage_factor(leverage: float) -> float:
    """Normalize leverage to weight factor (0-1)
    
    Higher leverage = higher conviction (but capped at 200)
    
    Args:
        leverage: Trade leverage
        
    Returns:
        Factor 0-1, clamped
    """
    # Scale: 1x = 0.1, 20x = 0.5, 200x = 1.0
    factor = min(leverage / 200.0, 1.0)
    return min(max(factor, 0.0), 1.0)


def recency_factor(
    timestamp: datetime,
    now: datetime = None,
    window_minutes: int = 15
) -> float:
    """Decay factor based on trade age (0-1)
    
    1.0 when fresh, decays toward 0.0 at edge of window.
    
    Args:
        timestamp: Trade timestamp
        now: Current time (default utcnow)
        window_minutes: Decay window
        
    Returns:
        Factor 0-1
    """
    if now is None:
        now = datetime.utcnow()
    
    age = (now - timestamp).total_seconds() / 60.0  # minutes
    
    if age < 0:
        return 1.0
    if age >= window_minutes:
        return 0.0
    
    # Linear decay: 1.0 -> 0.0
    decay = 1.0 - (age / window_minutes)
    return min(max(decay, 0.0), 1.0)


def trade_weight(
    trade: MWTTrade,
    profile: WalletProfile = None,
    now: datetime = None,
    window_minutes: int = 15
) -> float:
    """Compute trade weight for conviction (0-1)
    
    Formula: weight = wallet_score*0.4 + log(size_usd)*0.3 + leverage_factor*0.2 + recency_factor*0.1
    
    Args:
        trade: MWTTrade
        profile: WalletProfile (optional, defaults to neutral)
        now: Current time
        window_minutes: Recency window
        
    Returns:
        Weight 0-1
    """
    # Use default profile if not provided
    if profile is None:
        profile = WalletProfile(wallet_id=trade.wallet_id)
    
    # Component scores
    wallet_sc = wallet_score(profile)
    
    # Normalize size (log scale: 1000 USD = 0.3, 100k = 0.7)
    log_size = math.log10(max(trade.size_usd, 10))
    size_factor = min(log_size / 5.0, 1.0)  # log(100k) = 5
    
    lev_factor = leverage_factor(trade.leverage)
    rec_factor = recency_factor(trade.timestamp, now, window_minutes)
    
    weight = (
        wallet_sc * 0.4 +
        size_factor * 0.3 +
        lev_factor * 0.2 +
        rec_factor * 0.1
    )
    
    return min(max(weight, 0.0), 1.0)
