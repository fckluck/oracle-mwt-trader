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
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /health` - Server health check
- `GET /assets` - List tracked assets
- `GET /conviction` - Current conviction state
- `GET /wallets` - Registered wallets
- `POST /events` - Ingest wallet events (mock)

## Documentation

- [System Specification](docs/SYSTEM_SPEC.md) - Architecture and design
- [Phase 1 Build Plan](docs/PHASE_1_BUILD_PLAN.md) - Development roadmap

## Development

This project is in **Phase 1** (visibility & normalization). Live trading execution is planned for future phases.

### Key Constraints

- ✋ No live trading
- ✋ No real API keys
- ✋ No wallet private keys or seeds
- ✋ No exchange secrets or funded credentials
- ✅ Mock data for development and testing

## License

Proprietary - Oracle MWT Trader

## Contributing

See [PHASE_1_BUILD_PLAN.md](docs/PHASE_1_BUILD_PLAN.md) for development guidelines.
