"""
Paper Trading Simulator

Opens and manages simulated positions from signals.
"""

from paper.portfolio import PaperPortfolio
from mwt.models import ConvictionSignal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PaperSimulator:
    """Simulates paper trades from conviction signals"""
    
    def __init__(self, portfolio: PaperPortfolio = None):
        """Initialize simulator
        
        Args:
            portfolio: PaperPortfolio (creates new if not provided)
        """
        self.portfolio = portfolio or PaperPortfolio()
        self.simulated_trades = []
    
    def trade_signal(
        self,
        signal: ConvictionSignal,
        probe_size_usd: float = 50.0,
    ) -> dict:
        """Trade conviction signal
        
        Opens paper probe if portfolio can trade.
        
        Args:
            signal: ConvictionSignal
            probe_size_usd: Probe size in USD
            
        Returns:
            Trade result dict
        """
        if not self.portfolio.can_trade():
            logger.warning(f"Cannot trade signal - profit cap hit")
            return {
                "status": "rejected",
                "reason": "Daily profit cap reached",
            }
        
        position = self.portfolio.open_probe(
            asset=signal.asset.value,
            side=signal.direction.value,
            leverage=1.0,  # Default 1x for probes
            size_usd=probe_size_usd,
            entry_price=signal.avg_entry,
        )
        
        if not position:
            return {"status": "failed", "reason": "Could not open position"}
        
        result = {
            "status": "opened",
            "position_id": position.position_id,
            "asset": signal.asset.value,
            "side": signal.direction.value,
            "entry_price": signal.avg_entry,
            "size_usd": probe_size_usd,
            "conviction": signal.conviction_score,
            "signal_timestamp": signal.last_seen.isoformat(),
        }
        
        self.simulated_trades.append(result)
        logger.info(f"Paper trade opened: {result}")
        
        return result
    
    def get_status(self) -> dict:
        """Get simulator status"""
        return {
            "balance": self.portfolio.get_balance(),
            "realized_pnl": self.portfolio.realized_pnl,
            "open_positions": len(self.portfolio.open_positions),
            "closed_positions": len(self.portfolio.closed_positions),
            "daily_limit_remaining": self.portfolio.daily_profit_cap - self.portfolio.realized_pnl,
            "can_trade": self.portfolio.can_trade(),
        }
