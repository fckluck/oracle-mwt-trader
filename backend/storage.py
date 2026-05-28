"""
Storage abstraction for wallet events and MWT objects
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.models import WalletEvent, MWTObject
import uuid


class StorageBackend(ABC):
    """Abstract storage backend interface"""
    
    @abstractmethod
    async def store_event(self, event: WalletEvent) -> str:
        """Store a wallet event, return event_id"""
        pass
    
    @abstractmethod
    async def get_events(
        self,
        asset: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[WalletEvent]:
        """Retrieve events with optional filtering"""
        pass
    
    @abstractmethod
    async def store_mwt_object(self, mwt: MWTObject) -> str:
        """Store an MWT object, return mwt_id"""
        pass
    
    @abstractmethod
    async def get_mwt_objects(
        self,
        asset: Optional[str] = None,
        limit: int = 50,
    ) -> List[MWTObject]:
        """Retrieve MWT objects with optional filtering"""
        pass
    
    @abstractmethod
    async def register_wallet(
        self,
        wallet_address: str,
        venue: str,
        nickname: Optional[str] = None,
    ) -> str:
        """Register a wallet, return wallet_id"""
        pass
    
    @abstractmethod
    async def get_wallets(self) -> List[str]:
        """Retrieve all registered wallet addresses"""
        pass
    
    @abstractmethod
    async def clear(self):
        """Clear all data (for testing)"""
        pass


class MemoryStorage(StorageBackend):
    """In-memory storage backend for Phase 1 development"""
    
    def __init__(self):
        self.events: Dict[str, WalletEvent] = {}
        self.mwt_objects: Dict[str, MWTObject] = {}
        self.wallets: Dict[str, str] = {}  # wallet_id -> wallet_address
        self.wallet_by_address: Dict[str, str] = {}  # wallet_address -> wallet_id
    
    async def store_event(self, event: WalletEvent) -> str:
        """Store event in memory"""
        event_id = event.event_id
        self.events[event_id] = event
        return event_id
    
    async def get_events(
        self,
        asset: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[WalletEvent]:
        """Retrieve events with filtering"""
        events = list(self.events.values())
        
        if asset:
            events = [e for e in events if e.asset == asset]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Sort by timestamp descending (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    async def store_mwt_object(self, mwt: MWTObject) -> str:
        """Store MWT object in memory"""
        mwt_id = mwt.mwt_id
        self.mwt_objects[mwt_id] = mwt
        return mwt_id
    
    async def get_mwt_objects(
        self,
        asset: Optional[str] = None,
        limit: int = 50,
    ) -> List[MWTObject]:
        """Retrieve MWT objects with filtering"""
        objects = list(self.mwt_objects.values())
        
        if asset:
            objects = [m for m in objects if m.asset == asset]
        
        # Sort by cluster_end descending (most recent first)
        objects.sort(key=lambda m: m.cluster_end, reverse=True)
        
        return objects[:limit]
    
    async def register_wallet(
        self,
        wallet_address: str,
        venue: str,
        nickname: Optional[str] = None,
    ) -> str:
        """Register a wallet"""
        # Check if already registered
        if wallet_address in self.wallet_by_address:
            return self.wallet_by_address[wallet_address]
        
        wallet_id = str(uuid.uuid4())
        self.wallets[wallet_id] = wallet_address
        self.wallet_by_address[wallet_address] = wallet_id
        
        return wallet_id
    
    async def get_wallets(self) -> List[str]:
        """Get all wallet addresses"""
        return list(self.wallet_by_address.keys())
    
    async def clear(self):
        """Clear all data"""
        self.events.clear()
        self.mwt_objects.clear()
        self.wallets.clear()
        self.wallet_by_address.clear()


# Global storage instance
_storage: Optional[StorageBackend] = None


def get_storage() -> StorageBackend:
    """Get global storage instance"""
    global _storage
    if _storage is None:
        _storage = MemoryStorage()
    return _storage


async def init_storage(backend: StorageBackend):
    """Initialize storage backend"""
    global _storage
    _storage = backend
