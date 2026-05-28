"""
Conviction Detection Engine - Identify directional conviction from smart money
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from backend.models import ConvictionSignal
from backend.storage import get_storage

logger = logging.getLogger(__name__)


class ConvictionEngine:
    """Detects directional conviction from clustered wallet activity"""
    
    def __init__(
        self,
        window_minutes: int = 60,
        min_cluster_size: int = 2,
        threshold: float = 0.65,
    ):
        """Initialize conviction engine
        
        Args:
            window_minutes: Time window for conviction analysis
            min_cluster_size: Minimum events to consider
            threshold: Conviction threshold (0.0-1.0)
        """
        self.window_minutes = window_minutes
        self.min_cluster_size = min_cluster_size
        self.threshold = threshold
    
    async def compute_strongest_conviction(self) -> Optional[Dict]:
        """Compute strongest conviction signal across all assets
        
        Returns:
            Conviction signal or None if insufficient data
        """
        try:
            storage = get_storage()
            
            # Get recent MWT objects
            mwt_objects = await storage.get_mwt_objects(asset=None, limit=200)
            
            if not mwt_objects:
                logger.debug("No MWT objects found for conviction analysis")
                return None
            
            # Filter by time window and conviction threshold
            window_start = datetime.utcnow() - timedelta(minutes=self.window_minutes)
            
            significant_objects = [
                m for m in mwt_objects
                if (m.cluster_end >= window_start and
                    m.conviction_score >= self.threshold and
                    m.wallet_count >= self.min_cluster_size)
            ]
            
            if not significant_objects:
                logger.debug("No significant conviction signals found")
                return None
            
            # Aggregate conviction by asset and direction
            conviction_state = self._aggregate_conviction(significant_objects)
            
            logger.info(
                f"🎯 Conviction detected: {conviction_state['asset']} "
                f"{conviction_state['direction']} "
                f"(score: {conviction_state['conviction_score']:.2f})"
            )
            
            return conviction_state
            
        except Exception as e:
            logger.error(f"❌ Conviction computation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def compute_asset_conviction(self, asset: str) -> Optional[Dict]:
        """Compute conviction for specific asset
        
        Args:
            asset: Asset to analyze
            
        Returns:
            Conviction signal or None
        """
        try:
            storage = get_storage()
            
            # Get recent MWT objects for this asset
            mwt_objects = await storage.get_mwt_objects(asset=asset, limit=200)
            
            if not mwt_objects:
                logger.debug(f"No MWT objects found for {asset}")
                return None
            
            # Filter by time window and conviction threshold
            window_start = datetime.utcnow() - timedelta(minutes=self.window_minutes)
            
            significant_objects = [
                m for m in mwt_objects
                if (m.cluster_end >= window_start and
                    m.conviction_score >= self.threshold and
                    m.wallet_count >= self.min_cluster_size)
            ]
            
            if not significant_objects:
                logger.debug(f"No significant conviction signals for {asset}")
                return None
            
            # Aggregate
            conviction_state = self._aggregate_conviction(significant_objects)
            
            return conviction_state
            
        except Exception as e:
            logger.error(f"❌ Asset conviction computation failed: {e}")
            return None
    
    def _aggregate_conviction(self, mwt_objects: List) -> Dict:
        """Aggregate conviction from multiple MWT objects
        
        Phase 1: Simple max-conviction strategy
        
        Args:
            mwt_objects: List of significant MWT objects
            
        Returns:
            Aggregated conviction state
        """
        # Find strongest conviction signal
        strongest = max(mwt_objects, key=lambda m: m.conviction_score)
        
        # Count supporting events for this asset+direction
        supporting = [
            m for m in mwt_objects
            if m.asset == strongest.asset and m.direction == strongest.direction
        ]
        
        total_wallets = sum(m.wallet_count for m in supporting)
        supporting_clusters = len(supporting)
        total_events = sum(m.event_count for m in supporting)
        
        confidence = self._compute_confidence(total_wallets, supporting_clusters)
        
        conviction_state = {
            "asset": strongest.asset,
            "direction": strongest.direction,
            "conviction_score": strongest.conviction_score,
            "wallet_count": total_wallets,
            "confidence": confidence,
            "cluster_count": supporting_clusters,
            "supporting_events": total_events,
            "timestamp": datetime.utcnow(),
        }
        
        return conviction_state
    
    def _compute_confidence(self, wallet_count: int, cluster_count: int) -> float:
        """Compute confidence metric
        
        Args:
            wallet_count: Total unique wallets
            cluster_count: Number of supporting clusters
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple model: confidence based on wallet diversity
        wallet_confidence = min(wallet_count / 20, 1.0)
        cluster_confidence = min(cluster_count / 5, 1.0)
        
        return (wallet_confidence * 0.6) + (cluster_confidence * 0.4)
