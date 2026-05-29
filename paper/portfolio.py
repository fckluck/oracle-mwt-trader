"""
Paper Portfolio Management

Simulated portfolio for paper trading.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PaperPosition(BaseModel):
    """Simulated open position"""
    
    position_id: str
    asset: str
    side: str
    leverage: float
    size_usd: float
    entry_price: float
    entry_time: datetime
    current_price: float = None
    pnl_usd: float = 0.0
    pnl_pct: float = 0.0


class PaperPortfolio:
    """Simulated portfolio tracker"""
    
    def __init__(
        self,
        starting_balance: float = 100000.0,
        daily_profit_cap: float = 10000.0,
    ):
        """Initialize portfolio
        
        Args:
            starting_balance: Starting account balance
            daily_profit_cap: Daily profit limit
        """
        self.starting_balance = starting_balance
        self.daily_profit_cap = daily_profit_cap
        self.realized_pnl = 0.0
        self.open_positions: Dict[str, PaperPosition] = {}
        self.closed_positions: List[PaperPosition] = []
        self.trades_count = 0
    
    def can_trade(self) -> bool:
        """Check if can open new trades
        
        Returns False if daily profit cap hit.
        """
        if self.realized_pnl >= self.daily_profit_cap:
            logger.warning(f"Daily profit cap {self.daily_profit_cap} reached")
            return False
        return True
    
    def open_probe(
        self,
        asset: str,
        side: str,
        leverage: float,
        size_usd: float = 50.0,
        entry_price: float = 1.0,
    ) -> Optional[PaperPosition]:
        """Open paper probe position
        
        Args:
            asset: Asset
            side: long/short
            leverage: Leverage
            size_usd: Position size
            entry_price: Entry price
            
        Returns:
            PaperPosition or None if can't trade
        """
        if not self.can_trade():
            return None
        
        position_id = f"probe_{self.trades_count}"
        self.trades_count += 1
        
        position = PaperPosition(
            position_id=position_id,
            asset=asset,
            side=side,
            leverage=leverage,
            size_usd=size_usd,
            entry_price=entry_price,
            entry_time=datetime.utcnow(),
            current_price=entry_price,
        )
        
        self.open_positions[position_id] = position
        logger.info(f"Opened probe: {position_id} {asset} {side} {size_usd} USD @ {entry_price}")
        
        return position
    
    def close_position(
        self,
        position_id: str,
        exit_price: float,
    ) -> Optional[Dict]:
        """Close paper position
        
        Args:
            position_id: Position ID
            exit_price: Exit price
            
        Returns:
            P&L dict or None
        """
        if position_id not in self.open_positions:
            return None
        
        pos = self.open_positions.pop(position_id)
        
        # Calculate P&L
        price_diff = exit_price - pos.entry_price
        if pos.side == "short":
            price_diff = -price_diff
        
        pnl_usd = (price_diff / pos.entry_price) * pos.size_usd * pos.leverage
        pnl_pct = (price_diff / pos.entry_price) * 100
        
        self.realized_pnl += pnl_usd
        
        pos.current_price = exit_price
        pos.pnl_usd = pnl_usd
        pos.pnl_pct = pnl_pct
        
        self.closed_positions.append(pos)
        
        logger.info(
            f"Closed {position_id}: "
            f"P&L {pnl_usd:+.2f} USD ({pnl_pct:+.2f}%)"
        )
        
        return {
            "pnl_usd": pnl_usd,
            "pnl_pct": pnl_pct,
            "realized_total": self.realized_pnl,
        }
    
    def get_balance(self) -> float:
        """Get current account balance"""
        return self.starting_balance + self.realized_pnl
