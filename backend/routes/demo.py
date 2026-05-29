"""
Demo Routes

Generate demo signals and data for testing.
"""

from fastapi import APIRouter
from conviction.engine import ConvictionEngine
from mwt.normalizer import normalize_raw_trade
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/signal")
async def demo_signal():
    """Generate and return demo conviction signal
    
    Seeds with demo whale + trader SOL LONG trades.
    Returns conviction signal if meets threshold.
    """
    engine = ConvictionEngine(
        min_score=settings.conviction_threshold,
        window_minutes=settings.window_minutes,
    )
    
    # Load demo trades
    for raw_data, profile in ConvictionEngine.demo_trades():
        try:
            trade = normalize_raw_trade(raw_data)
            engine.add_trade(trade, profile)
        except Exception as e:
            logger.error(f"Failed to add demo trade: {e}")
            return {"status": "error", "message": str(e)}
    
    # Build signals
    signals = engine.build_signals()
    
    if not signals:
        return {
            "status": "no_signal",
            "message": "No signals above threshold",
            "threshold": settings.conviction_threshold,
        }
    
    signal = signals[0]  # Return strongest
    
    return {
        "status": "signal_generated",
        "signal": {
            "asset": signal.asset.value,
            "direction": signal.direction.value,
            "total_size_usd": signal.total_size_usd,
            "avg_entry": signal.avg_entry,
            "wallet_count": signal.wallet_count,
            "conviction_score": signal.conviction_score,
            "platforms": signal.platforms,
            "first_seen": signal.first_seen.isoformat(),
            "last_seen": signal.last_seen.isoformat(),
        },
    }
