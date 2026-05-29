# Oracle MWT Trader

A multi-platform perp wallet-tracking system for detecting directional conviction through smart money analysis.

## Mission

Oracle MWT Trader tracks smart money across perp platforms by:
- Ingesting wallet events from multiple venues
- Normalizing trades into universal MWT (Multi-Wallet Tracking) objects
- Detecting directional conviction from clustered wallet activity
- Selecting the asset with highest current conviction
- **Phase 1**: Visibility only (no live trading)

> Core philosophy: The bot does not fear being wrong. It fears not recognizing invalidation fast enough.

## Phase 1 Active Assets

- SOL
- BTC
- ETH
- HYPE

## Phase 1 Scope

✅ Mock/live-ready wallet event ingestion  
✅ Universal MWT object normalization  
✅ Conviction cluster computation  
✅ API endpoints for visibility  
❌ Live trading execution  
❌ Real API keys or wallet credentials  

## Project Structure

```
oracle-mwt-trader/
├── backend/          # FastAPI server, config, models
├── mwt/              # Multi-Wallet Tracking normalization
├── conviction/       # Conviction engine
├── docs/             # System specifications and planning
└── requirements.txt  # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- pip or uv

### Installation

```bash
# Clone and navigate to project
cd oracle-mwt-trader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Running the Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

## Phase 1.5 Hardened API Endpoints

### Health & Status

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/assets
```

### Database Management

```bash
# Seed with mock data
curl -X POST http://127.0.0.1:8000/seed

# Clear all data
curl -X DELETE http://127.0.0.1:8000/events
```

### Event Ingestion

```bash
# Primary endpoint (alias)
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "venue": "drift",
    "wallet_address": "0x123...",
    "asset": "SOL",
    "direction": "long",
    "size": 10.5,
    "entry_price": 140.50,
    "timestamp": "2026-05-28T15:30:00Z",
    "tx_hash": "0xdef456..."
  }'

# Legacy endpoint (still supported)
curl -X POST http://127.0.0.1:8000/events/ingest \
  -H "Content-Type: application/json" \
  -d '{...}'

# Retrieve events
curl http://127.0.0.1:8000/events
curl http://127.0.0.1:8000/events?asset=SOL&limit=50
```

### MWT & Conviction

```bash
# Get all MWT objects
curl http://127.0.0.1:8000/mwt

# Get strongest conviction signal
curl http://127.0.0.1:8000/conviction

# Get all conviction candidates above threshold
curl http://127.0.0.1:8000/conviction/all

# Get selected asset with signal status
curl http://127.0.0.1:8000/selected-asset
```

## API Response Examples

### POST /events
```json
{
  "event_id": "evt-123",
  "mwt_id": "mwt-456",
  "conviction_score": 0.78,
  "timestamp": "2026-05-28T15:30:00Z",
  "status": "ingested"
}
```

### DELETE /events
```json
{
  "status": "cleared",
  "timestamp": "2026-05-28T15:30:00Z"
}
```

### GET /mwt
```json
{
  "mwt_objects": [
    {
      "mwt_id": "mwt-123",
      "asset": "SOL",
      "direction": "long",
      "conviction_score": 0.78,
      "wallet_count": 8,
      "avg_size": 12.3,
      "cluster_start": "2026-05-28T15:20:00Z",
      "cluster_end": "2026-05-28T15:35:00Z",
      "event_count": 8
    }
  ],
  "count": 1
}
```

### GET /conviction/all
```json
{
  "candidates": [
    {
      "mwt_id": "mwt-123",
      "asset": "SOL",
      "direction": "long",
      "conviction_score": 0.78,
      "wallet_count": 8,
      "event_count": 8
    }
  ],
  "count": 1,
  "threshold": 0.65,
  "window_minutes": 60,
  "timestamp": "2026-05-28T15:30:00Z"
}
```

### GET /selected-asset
```json
{
  "selected": true,
  "selected_asset": "SOL",
  "conviction": {
    "asset": "SOL",
    "direction": "long",
    "conviction_score": 0.78,
    "wallet_count": 15,
    "confidence": 0.82,
    "cluster_count": 2,
    "supporting_events": 16,
    "timestamp": "2026-05-28T15:30:00Z"
  },
  "timestamp": "2026-05-28T15:30:00Z"
}
```

## Documentation

- [System Specification](docs/SYSTEM_SPEC.md) - Architecture and design
- [Phase 1 Build Plan](docs/PHASE_1_BUILD_PLAN.md) - Development roadmap

## Development

This project is in **Phase 1.5** (visibility & hardening). Live trading execution is planned for future phases.

### Key Constraints

- ✋ No live trading
- ✋ No real API keys
- ✋ No wallet private keys or seeds
- ✋ No exchange secrets or funded credentials
- ✅ Mock data for development and testing

### Testing with cURL

```bash
# Full workflow
uvicorn backend.main:app --reload &

# Seed database
curl -X POST http://127.0.0.1:8000/seed

# Check events
curl http://127.0.0.1:8000/events | jq

# Get conviction
curl http://127.0.0.1:8000/conviction | jq

# Get candidates
curl http://127.0.0.1:8000/conviction/all | jq

# Get selected asset
curl http://127.0.0.1:8000/selected-asset | jq

# Clear all
curl -X DELETE http://127.0.0.1:8000/events

# Verify clear
curl http://127.0.0.1:8000/events | jq
```

## License

Proprietary - Oracle MWT Trader

## Contributing

See [PHASE_1_BUILD_PLAN.md](docs/PHASE_1_BUILD_PLAN.md) for development guidelines.
