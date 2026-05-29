"""
Jupiter Listener (Stub)

Placeholder for Jupiter swap integration.
"""

import logging
from typing import List
from mwt.models import MWTTrade

logger = logging.getLogger(__name__)


def listen_jupiter() -> List[MWTTrade]:
    """Listen for Jupiter swaps
    
    Phase 1: Returns empty list (placeholder)
    """
    logger.debug("Jupiter listener stub - no live data yet")
    return []
