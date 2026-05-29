"""
Ostium Listener (Stub)

Placeholder for Ostium integration.
"""

import logging
from typing import List
from mwt.models import MWTTrade

logger = logging.getLogger(__name__)


def listen_ostium() -> List[MWTTrade]:
    """Listen for Ostium trades
    
    Phase 1: Returns empty list (placeholder)
    """
    logger.debug("Ostium listener stub - no live data yet")
    return []
