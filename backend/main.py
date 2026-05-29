"""
FastAPI application entry point for Oracle MWT Trader
"""

import logging
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import settings
from backend.models import (
    HealthResponse,
    SeedResponse,
    ConvictionSignal,
    IngestEventRequest,
    IngestEventResponse,
    WalletEvent,
)
from backend.storage import get_storage
from backend.seed import seed_database
from mwt.normalizer import MWTNormalizer
from conviction.engine import ConvictionEngine
import uuid

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Global instances
normalizer: MWTNormalizer = None
conviction_engine: ConvictionEngine = None
start_time: datetime = datetime.utcnow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global normalizer, conviction_engine, start_time
    
    logger.info(f"🚀 Oracle MWT Trader v{settings.api_version} starting...")
    logger.info(f"📊 Active assets: {', '.join(settings.active_assets)}")
    logger.info(f"💾 Storage: {settings.storage_type}")
    logger.info(f"📈 Conviction window: {settings.conviction_window_minutes} minutes")
    
    # Initialize components
    normalizer = MWTNormalizer(
        cluster_window_minutes=settings.conviction_window_minutes,
        min_cluster_size=settings.min_cluster_size,
    )
    conviction_engine = ConvictionEngine(
        window_minutes=settings.conviction_window_minutes,
        min_cluster_size=settings.min_cluster_size,
        threshold=settings.conviction_threshold,
    )
    
    start_time = datetime.utcnow()
    
    logger.info("✅ Oracle MWT Trader initialized")
    
    yield
    
    logger.info("🛑 Oracle MWT Trader shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Oracle MWT Trader",
    description="Multi-Wallet Tracking System for Smart Money Analysis",
    version=settings.api_version,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Shared Helpers
# ============================================================================

async def _ingest_event(request: IngestEventRequest) -> IngestEventResponse:
    """Shared event ingestion logic
    
    Args:
        request: IngestEventRequest with wallet event data
        
    Returns:
        IngestEventResponse with event and MWT details
    """
    storage = get_storage()
    
    # Create WalletEvent
    event = WalletEvent(
        event_id=str(uuid.uuid4()),
        venue=request.venue,
        wallet_address=request.wallet_address,
        asset=request.asset,
        direction=request.direction,
        size=request.size,
        entry_price=request.entry_price,
        timestamp=request.timestamp,
        tx_hash=request.tx_hash,
        metadata=request.metadata or {},
    )
    
    # Store event
    event_id = await storage.store_event(event)
    
    # Normalize to MWT
    mwt_id = None
    conviction_score = None
    try:
        mwt_object = await normalizer.normalize(event)
        if mwt_object:
            mwt_id = await storage.store_mwt_object(mwt_object)
            conviction_score = mwt_object.conviction_score
            
            logger.info(
                f"📊 Created MWT object {mwt_id} with conviction {conviction_score:.2f}"
            )
    except Exception as e:
        logger.error(f"❌ Normalization error: {e}")
    
    logger.info(f"✅ Ingested event {event_id} from {request.wallet_address}")
    
    return IngestEventResponse(
        event_id=event_id,
        mwt_id=mwt_id,
        conviction_score=conviction_score,
        timestamp=datetime.utcnow(),
        status="ingested",
    )


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        timestamp=datetime.utcnow(),
        uptime_seconds=uptime,
    )


@app.get("/assets")
async def get_assets():
    """Get list of tracked assets"""
    return {
        "assets": settings.active_assets,
        "count": len(settings.active_assets),
    }


# ============================================================================
# Seed Endpoint
# ============================================================================

@app.post("/seed", response_model=SeedResponse)
async def seed():
    """Seed database with mock wallet events"""
    result = await seed_database()
    
    return SeedResponse(
        status="seeded",
        events_created=result["events_created"],
        wallets_registered=result["wallets_registered"],
        timestamp=datetime.utcnow(),
    )


# ============================================================================
# Event Endpoints
# ============================================================================

@app.post("/events/ingest", response_model=IngestEventResponse)
async def ingest_event(request: IngestEventRequest):
    """Ingest a wallet event (legacy endpoint)"""
    return await _ingest_event(request)


@app.post("/events", response_model=IngestEventResponse)
async def ingest_event_alias(request: IngestEventRequest):
    """Ingest a wallet event"""
    return await _ingest_event(request)


@app.get("/events")
async def get_events(
    asset: str = None,
    limit: int = 100,
):
    """Retrieve wallet events"""
    if limit > 1000:
        limit = 1000
    
    storage = get_storage()
    events = await storage.get_events(asset=asset, limit=limit)
    
    return {
        "events": events,
        "count": len(events),
    }


@app.delete("/events")
async def delete_events():
    """Clear all events, MWT objects, and wallets from storage"""
    storage = get_storage()
    await storage.clear()
    
    logger.info("🗑️  Cleared all events, MWT objects, and wallets")
    
    return {
        "status": "cleared",
        "timestamp": datetime.utcnow(),
    }


# ============================================================================
# MWT Endpoints
# ============================================================================

@app.get("/mwt")
async def get_mwt_objects():
    """Get all stored MWT objects"""
    storage = get_storage()
    mwt_objects = await storage.get_mwt_objects(asset=None, limit=500)
    
    return {
        "mwt_objects": mwt_objects,
        "count": len(mwt_objects),
    }


# ============================================================================
# Conviction Endpoints
# ============================================================================

@app.get("/conviction")
async def get_conviction():
    """Get current conviction state (strongest signal)"""
    if not conviction_engine:
        raise HTTPException(status_code=503, detail="Conviction engine not initialized")
    
    conviction = await conviction_engine.compute_strongest_conviction()
    
    if not conviction:
        return {
            "conviction": None,
            "message": "No conviction signals detected",
            "timestamp": datetime.utcnow(),
        }
    
    return {
        "conviction": conviction,
        "timestamp": datetime.utcnow(),
    }


@app.get("/conviction/all")
async def get_all_conviction_candidates():
    """Get all active conviction candidates above threshold
    
    Returns all MWT objects meeting conviction criteria, sorted by conviction score
    """
    if not conviction_engine:
        raise HTTPException(status_code=503, detail="Conviction engine not initialized")
    
    storage = get_storage()
    
    # Get recent MWT objects
    mwt_objects = await storage.get_mwt_objects(asset=None, limit=500)
    
    if not mwt_objects:
        return {
            "candidates": [],
            "count": 0,
            "threshold": conviction_engine.threshold,
            "window_minutes": conviction_engine.window_minutes,
            "timestamp": datetime.utcnow(),
        }
    
    # Filter by conviction threshold and cluster size
    from datetime import timedelta
    window_start = datetime.utcnow() - timedelta(minutes=conviction_engine.window_minutes)
    
    candidates = [\n        m for m in mwt_objects
        if (m.cluster_end >= window_start and
            m.conviction_score >= conviction_engine.threshold and
            m.wallet_count >= conviction_engine.min_cluster_size)
    ]
    
    # Sort by conviction score descending
    candidates.sort(key=lambda m: m.conviction_score, reverse=True)
    
    logger.info(f"📊 Found {len(candidates)} conviction candidates above threshold {conviction_engine.threshold:.2f}")
    
    return {
        "candidates": candidates,
        "count": len(candidates),
        "threshold": conviction_engine.threshold,
        "window_minutes": conviction_engine.window_minutes,
        "timestamp": datetime.utcnow(),
    }


@app.get("/selected-asset")
async def selected_asset():
    """Get highest conviction asset"""
    if not conviction_engine:
        raise HTTPException(status_code=503, detail="Conviction engine not initialized")
    
    conviction = await conviction_engine.compute_strongest_conviction()
    
    if not conviction:
        return {
            "selected": False,
            "selected_asset": None,
            "conviction": None,
            "message": "No conviction signal above threshold",
            "timestamp": datetime.utcnow(),
        }
    
    return {
        "selected": True,
        "selected_asset": conviction["asset"],
        "conviction": conviction,
        "timestamp": datetime.utcnow(),
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Oracle MWT Trader",
        "version": settings.api_version,
        "description": "Multi-Wallet Tracking System for Smart Money Analysis",
        "docs": "/docs" if settings.enable_docs else None,
        "health": "/health",
        "endpoints": {
            "health": "GET /health",
            "assets": "GET /assets",
            "seed": "POST /seed",
            "ingest": "POST /events/ingest",
            "ingest_alias": "POST /events",
            "get_events": "GET /events",
            "delete_events": "DELETE /events",
            "mwt": "GET /mwt",
            "conviction": "GET /conviction",
            "conviction_all": "GET /conviction/all",
            "selected_asset": "GET /selected-asset",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
