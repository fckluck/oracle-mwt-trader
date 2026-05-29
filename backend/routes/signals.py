"""
Signals Routes

List and manage conviction signals.
"""

from fastapi import APIRouter
from paper.simulator import PaperSimulator
from conviction.engine import ConvictionEngine
from mwt.normalizer import normalize_raw_trade
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])

# In-memory simulator for demo
simulator = PaperSimulator()


@router.get("/")
async def list_signals():
    """List current signals (empty in Phase 1 without live data)"""
    return {
        "signals": [],
        "count": 0,
        "message": "No live data - use /demo/signal for demo",
    }


@router.post("/demo-paper")
async def demo_paper():
    """Create demo signal and open paper probe
    
    Demonstrates full workflow:
    1. Generate demo trades
    2. Build conviction signal
    3. Open paper probe
    4. Return status
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
        }
    
    signal = signals[0]
    
    # Trade signal with paper simulator
    trade_result = simulator.trade_signal(signal, probe_size_usd=50.0)
    
    return {
        "status": "success",
        "signal": {
            "asset": signal.asset.value,
            "direction": signal.direction.value,
            "conviction": signal.conviction_score,
        },
        "paper_trade": trade_result,
        "portfolio_status": simulator.get_status(),
    }
