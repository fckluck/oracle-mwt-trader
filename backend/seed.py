"""
Seed database with mock wallet events for testing
"""

import logging
from datetime import datetime, timedelta
from backend.models import WalletEvent
from backend.storage import get_storage
from mwt.sample_events import SampleEventGenerator

logger = logging.getLogger(__name__)


async def seed_database():
    """Populate database with mock data for testing"""
    storage = get_storage()
    
    # Clear existing data
    await storage.clear()
    
    logger.info("🌱 Seeding database with mock events...")
    
    # Generate coordinated conviction clusters
    clusters = [
        ("SOL", "long", 8),
        ("BTC", "short", 5),
        ("ETH", "long", 6),
        ("SOL", "short", 4),
        ("HYPE", "long", 7),
    ]
    
    event_count = 0
    wallet_addresses = set()
    
    now = datetime.utcnow()
    
    for asset, direction, wallet_count in clusters:
        # Generate cluster with time spread
        for i in range(wallet_count):
            # Spread events over 30 minutes
            offset_minutes = (i * 30) // wallet_count
            event_time = now - timedelta(minutes=offset_minutes)
            
            event = SampleEventGenerator.generate_event(
                asset=asset,
                direction=direction,
                timestamp=event_time,
            )
            
            event_id = await storage.store_event(event)
            wallet_addresses.add(event.wallet_address)
            event_count += 1
            
            logger.debug(f"  Stored event {event_id}: {asset} {direction} from {event.wallet_address}")
    
    # Register wallets
    wallet_count = 0
    for wallet_address in wallet_addresses:
        await storage.register_wallet(
            wallet_address=wallet_address,
            venue="drift",
        )
        wallet_count += 1
        logger.debug(f"  Registered wallet {wallet_address}")
    
    logger.info(f"✅ Seeded {event_count} events from {wallet_count} wallets")
    
    return {
        "events_created": event_count,
        "wallets_registered": wallet_count,
    }
