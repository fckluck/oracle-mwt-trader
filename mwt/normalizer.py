"""
MWT Normalization - Convert venue-specific events to universal MWT objects
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
import uuid

from backend.models import WalletEvent, MWTObject
from backend.storage import get_storage

logger = logging.getLogger(__name__)


class MWTNormalizer:
    """Normalizes wallet events from different venues into MWT objects"""
    
    def __init__(
        self,
        cluster_window_minutes: int = 60,
        min_cluster_size: int = 2,
    ):
        """Initialize normalizer
        
        Args:
            cluster_window_minutes: Time window for clustering similar events
            min_cluster_size: Minimum number of events to form a cluster
        """
        self.cluster_window_minutes = cluster_window_minutes
        self.min_cluster_size = min_cluster_size
    
    async def normalize(self, event: WalletEvent) -> Optional[MWTObject]:
        """Normalize a wallet event into MWT object(s)
        
        Phase 1: Simple clustering by asset and direction within time window
        
        Args:
            event: Raw wallet event to normalize
            
        Returns:
            MWT object if sufficient cluster formed, None otherwise
        """
        try:
            # Get storage
            storage = get_storage()
            
            # Find recent events with same asset and direction
            window_start = event.timestamp - timedelta(minutes=self.cluster_window_minutes)
            
            recent_events = await storage.get_events(asset=event.asset, limit=1000)
            
            # Filter by direction and time window
            matching_events = [
                e for e in recent_events
                if (e.direction == event.direction and
                    e.timestamp >= window_start and
                    e.timestamp <= event.timestamp)
            ]
            
            # Add current event if not already included
            if event not in matching_events:
                matching_events.append(event)
            
            # Check if we have enough events to form a cluster
            if len(matching_events) < self.min_cluster_size:
                logger.debug(
                    f"📉 Insufficient cluster size for {event.asset} "
                    f"{event.direction}: {len(matching_events)}/{self.min_cluster_size}"
                )
                return None
            
            # Create MWT object
            mwt = self._create_mwt_object(event.asset, event.direction, matching_events)
            
            logger.info(
                f"✅ Created MWT: {event.asset} {event.direction} "
                f"({len(set(e.wallet_address for e in matching_events))} wallets, "
                f"conviction: {mwt.conviction_score:.2f})"
            )
            
            return mwt
            
        except Exception as e:
            logger.error(f"❌ Normalization failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_mwt_object(
        self,
        asset: str,
        direction: str,
        events: list,
    ) -> MWTObject:
        """Create an MWT object from clustered events
        
        Args:
            asset: Asset being traded
            direction: Trade direction (long/short)
            events: List of clustered events
            
        Returns:
            MWT object with computed metrics
        """
        # Remove duplicates by wallet
        unique_wallets = {}
        for event in events:
            if event.wallet_address not in unique_wallets:
                unique_wallets[event.wallet_address] = event
        
        unique_events = list(unique_wallets.values())
        wallet_count = len(unique_events)
        
        # Compute metrics
        avg_size = sum(e.size for e in unique_events) / wallet_count if wallet_count > 0 else 0
        
        # Compute venue distribution
        venue_distribution = {}
        for event in unique_events:
            venue = event.venue
            venue_distribution[venue] = venue_distribution.get(venue, 0) + 1
        
        # Compute conviction score (Phase 1 simple model)
        conviction_score = self._compute_conviction_score(wallet_count, avg_size)
        
        # Compute temporal bounds
        timestamps = [e.timestamp for e in unique_events]
        cluster_start = min(timestamps)
        cluster_end = max(timestamps)
        
        # Create MWT object
        mwt = MWTObject(
            mwt_id=str(uuid.uuid4()),
            asset=asset,
            direction=direction,
            conviction_score=conviction_score,
            wallet_count=wallet_count,
            avg_size=avg_size,
            venue_distribution=venue_distribution,
            cluster_start=cluster_start,
            cluster_end=cluster_end,
            event_count=len(unique_events),
        )
        
        return mwt
    
    def _compute_conviction_score(self, wallet_count: int, avg_size: float) -> float:
        """Compute conviction score
        
        Phase 1: Simple model based on wallet count and size
        
        Args:
            wallet_count: Number of unique wallets in cluster
            avg_size: Average position size
            
        Returns:
            Conviction score (0.0 to 1.0)
        """
        # Normalize by typical parameters
        max_wallets = 50
        max_size = 100.0
        
        wallet_factor = min(wallet_count / max_wallets, 1.0)
        size_factor = min(avg_size / max_size, 1.0)
        
        # Weighted average
        conviction_score = (wallet_factor * 0.6) + (size_factor * 0.4)
        
        return min(conviction_score, 1.0)
