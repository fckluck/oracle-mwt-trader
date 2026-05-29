"""
Hyperliquid Listener (Stub)

Placeholder for Hyperliquid perp market integration.
"""

import logging
from typing import List
from mwt.models import MWTTrade

logger = logging.getLogger(__name__)


def listen_hyperliquid() -> List[MWTTrade]:
    """Listen for Hyperliquid perp trades
    
    Phase 1: Returns empty list (placeholder)
    """
    logger.debug("Hyperliquid listener stub - no live data yet")
    return []
