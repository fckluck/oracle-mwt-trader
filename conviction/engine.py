"""
Conviction Engine

Clusters MWT trades and computes conviction signals.
"""

from conviction.scoring import trade_weight
from mwt.models import MWTTrade, ConvictionSignal, WalletProfile, Asset, Side, Platform
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConvictionEngine:
    """Clusters trades and emits conviction signals"""
    
    def __init__(
        self,
        min_score: float = 0.75,
        window_minutes: int = 15,
    ):
        """Initialize engine
        
        Args:
            min_score: Minimum conviction score to emit signal
            window_minutes: Clustering time window
        """
        self.min_score = min_score
        self.window_minutes = window_minutes
        self.trades: List[MWTTrade] = []
        self.profiles: Dict[str, WalletProfile] = {}
    
    def add_trade(
        self,
        trade: MWTTrade,
        profile: WalletProfile = None
    ) -> None:
        """Add trade to engine
        
        Args:
            trade: MWTTrade to add
            profile: Optional wallet profile
        """
        self.trades.append(trade)
        if profile:
            self.profiles[trade.wallet_id] = profile
        logger.debug(f"Added trade: {trade.asset} {trade.side} from {trade.wallet_id}")
    
    def build_signals(self, now: datetime = None) -> List[ConvictionSignal]:
        """Build conviction signals from current trades
        
        Clusters by asset and side within time window.
        Returns signals >= min_score.
        
        Args:
            now: Current time (default utcnow)
            
        Returns:
            List of ConvictionSignal
        """
        if now is None:
            now = datetime.utcnow()
        
        if not self.trades:
            logger.debug("No trades to cluster")
            return []
        
        # Filter trades within window
        window_start = now - timedelta(minutes=self.window_minutes)
        recent_trades = [
            t for t in self.trades
            if t.timestamp >= window_start
        ]
        
        if not recent_trades:
            logger.debug(f"No trades in {self.window_minutes}min window")
            return []
        
        # Cluster by asset and side
        clusters: Dict[tuple, List[MWTTrade]] = {}
        for trade in recent_trades:
            key = (trade.asset, trade.side)
            if key not in clusters:
                clusters[key] = []
            clusters[key].append(trade)
        
        # Build signals
        signals = []
        for (asset, side), cluster_trades in clusters.items():
            signal = self._build_signal(asset, side, cluster_trades, now)
            if signal and signal.conviction_score >= self.min_score:
                signals.append(signal)
                logger.info(
                    f"🎯 Signal: {asset} {side} "
                    f"conviction={signal.conviction_score:.2f} "
                    f"wallets={signal.wallet_count}"
                )
        
        return signals
    
    def _build_signal(
        self,
        asset: Asset,
        side: Side,
        trades: List[MWTTrade],
        now: datetime
    ) -> Optional[ConvictionSignal]:
        """Build single conviction signal
        
        Args:
            asset: Asset
            side: Side
            trades: Trades for cluster
            now: Current time
            
        Returns:
            ConvictionSignal or None
        """
        if not trades:
            return None
        
        # Compute weights
        weighted_entries = []
        total_weight = 0
        platforms = set()
        
        for trade in trades:
            profile = self.profiles.get(trade.wallet_id)
            weight = trade_weight(trade, profile, now, self.window_minutes)
            weighted_entries.append((trade.entry_price, weight))
            total_weight += weight
            platforms.add(trade.platform.value)
        
        if total_weight == 0:
            return None
        
        # Weighted avg entry
        avg_entry = sum(p * w for p, w in weighted_entries) / total_weight
        
        # Total size
        total_size = sum(t.size_usd for t in trades)
        
        # Wallet count
        wallet_count = len(set(t.wallet_id for t in trades))
        
        # Conviction score (weighted avg of individual trade weights)
        conviction_score = total_weight / len(trades)
        conviction_score = min(max(conviction_score, 0.0), 1.0)
        
        # Timestamps
        first_seen = min(t.timestamp for t in trades)
        last_seen = max(t.timestamp for t in trades)
        
        signal = ConvictionSignal(
            asset=asset,
            direction=side,
            total_size_usd=total_size,
            avg_entry=avg_entry,
            wallet_count=wallet_count,
            platforms=list(platforms),
            conviction_score=conviction_score,
            first_seen=first_seen,
            last_seen=last_seen,
            trades=trades,
        )
        
        return signal
    
    @staticmethod
    def demo_trades() -> List[tuple]:
        """Generate demo trades for testing
        
        Returns:
            List of (raw_data, profile) tuples
        """
        from mwt.models import WalletClass
        
        now = datetime.utcnow()
        
        return [
            # Whale 1: 20X Long SOL 79.90 size 600000 Ostium
            (
                {
                    "wallet_id": "whale_1",
                    "wallet_class": WalletClass.WHALE.value,
                    "asset": "SOL",
                    "side": "long",
                    "leverage": 20.0,
                    "size_usd": 600000,
                    "entry_price": 79.90,
                    "platform": "ostium",
                    "timestamp": now.isoformat(),
                },
                WalletProfile(
                    wallet_id="whale_1",
                    wallet_class=WalletClass.WHALE,
                    winrate=0.65,
                    avg_rr=2.5,
                    consistency=0.8,
                )
            ),
            # Active Trader 5: 40X Long SOL 81.24 size 25000 Jupiter
            (
                {
                    "wallet_id": "trader_5",
                    "wallet_class": WalletClass.ACTIVE_TRADER.value,
                    "asset": "SOL",
                    "side": "long",
                    "leverage": 40.0,
                    "size_usd": 25000,
                    "entry_price": 81.24,
                    "platform": "jupiter",
                    "timestamp": now.isoformat(),
                },
                WalletProfile(
                    wallet_id="trader_5",
                    wallet_class=WalletClass.ACTIVE_TRADER,
                    winrate=0.58,
                    avg_rr=1.8,
                    consistency=0.65,
                )
            ),
            # Active Trader 7: 40X Long SOL 82.10 size 42000 Hyperliquid
            (
                {
                    "wallet_id": "trader_7",
                    "wallet_class": WalletClass.ACTIVE_TRADER.value,
                    "asset": "SOL",
                    "side": "long",
                    "leverage": 40.0,
                    "size_usd": 42000,
                    "entry_price": 82.10,
                    "platform": "hyperliquid",
                    "timestamp": now.isoformat(),
                },
                WalletProfile(
                    wallet_id="trader_7",
                    wallet_class=WalletClass.ACTIVE_TRADER,
                    winrate=0.52,
                    avg_rr=1.6,
                    consistency=0.6,
                )
            ),
        ]
