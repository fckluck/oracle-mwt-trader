"""
Sample/mock wallet events for testing and development
"""

from datetime import datetime, timedelta
from typing import List
import random
import uuid


class SampleEventGenerator:
    """Generate realistic mock wallet events for testing"""
    
    # Sample wallet addresses (anonymous for privacy)
    SAMPLE_WALLETS = [
        "0x1234567890abcdef1234567890abcdef12345678",
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        "0xfedcfedcfedcfedcfedcfedcfedcfedcfedcfedc",
        "0x9876543210fedcba9876543210fedcba98765432",
        "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "0xcccccccccccccccccccccccccccccccccccccccc",
        "0xdddddddddddddddddddddddddddddddddddddddd",
        "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "0xffffffffffffffffffffffffffffffffffffffff",
    ]
    
    # Sample assets (Phase 1)
    ASSETS = ["SOL", "BTC", "ETH", "HYPE"]
    
    # Sample venues
    VENUES = ["dydx", "drift", "marinade"]
    
    # Asset price ranges (for realistic entry prices)
    ASSET_PRICES = {
        "SOL": (50, 200),
        "BTC": (30000, 70000),
        "ETH": (1500, 5000),
        "HYPE": (0.01, 1.0),
    }
    
    @classmethod
    def generate_event(
        cls,
        asset: str = None,
        direction: str = None,
        timestamp: datetime = None,
    ):
        """Generate a single mock event
        
        Args:
            asset: Asset to trade (random if None)
            direction: Trade direction (random if None)
            timestamp: Event timestamp (now if None)
            
        Returns:
            Mock WalletEvent dict
        """
        from backend.models import WalletEvent
        
        asset = asset or random.choice(cls.ASSETS)
        direction = direction or random.choice(["long", "short"])
        timestamp = timestamp or datetime.utcnow()
        
        venue = random.choice(cls.VENUES)
        wallet = random.choice(cls.SAMPLE_WALLETS)
        
        # Get realistic price range
        price_min, price_max = cls.ASSET_PRICES.get(asset, (1, 100))
        entry_price = random.uniform(price_min, price_max)
        
        # Size proportional to asset (rough heuristic)
        if asset == "BTC":
            size = random.uniform(0.01, 1.0)
        elif asset == "ETH":
            size = random.uniform(0.5, 10.0)
        else:
            size = random.uniform(1.0, 100.0)
        
        return WalletEvent(
            event_id=str(uuid.uuid4()),
            venue=venue,
            wallet_address=wallet,
            asset=asset,
            direction=direction,
            size=size,
            entry_price=entry_price,
            timestamp=timestamp,
            tx_hash=f"0x{uuid.uuid4().hex[:64]}",
            metadata={
                "source": "mock",
                "leverage": random.choice([1, 2, 3, 5]),
            },
        )
    
    @classmethod
    def generate_cluster(
        cls,
        asset: str,
        direction: str,
        wallet_count: int = 5,
    ) -> List:
        """Generate a cluster of coordinated events (smart money signal)
        
        Args:
            asset: Asset to cluster on
            direction: Common direction
            wallet_count: Number of unique wallets
            
        Returns:
            List of correlated events
        """
        now = datetime.utcnow()
        events = []
        
        for i in range(wallet_count):
            # Slight time spread (within 2 minutes)
            timestamp = now - timedelta(seconds=random.randint(0, 120))
            
            event = cls.generate_event(
                asset=asset,
                direction=direction,
                timestamp=timestamp,
            )
            events.append(event)
        
        return events
    
    @classmethod
    def generate_diverse_sample(cls, count: int = 20) -> List:
        """Generate a diverse sample of events across assets
        
        Args:
            count: Total events to generate
            
        Returns:
            List of diverse mock events
        """
        events = []
        now = datetime.utcnow()
        
        for i in range(count):
            # Spread over last hour
            timestamp = now - timedelta(minutes=random.randint(0, 60))
            
            event = cls.generate_event(timestamp=timestamp)
            events.append(event)
        
        return events


# Convenience functions
def generate_event(**kwargs):
    """Generate a single mock event"""
    return SampleEventGenerator.generate_event(**kwargs)


def generate_cluster(asset: str, direction: str, wallet_count: int = 5) -> List:
    """Generate a cluster of mock events"""
    return SampleEventGenerator.generate_cluster(asset, direction, wallet_count)


def generate_sample(count: int = 20) -> List:
    """Generate diverse mock events"""
    return SampleEventGenerator.generate_diverse_sample(count)
