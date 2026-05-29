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
✅ Paper trading simulation  
❌ Live trading execution  
❌ Real API keys or wallet credentials  

## Project Structure

```
oracle-mwt-trader/
├── backend/              # FastAPI server, config, routes
├── mwt/                  # Multi-Wallet Tracking models + normalization
├── conviction/           # Conviction scoring and clustering engine
├── market/               # Bias, structure, liquidation placeholders
├── storage/              # SQLite schema and DB helpers
├── paper/                # Paper portfolio + paper simulation
├── scripts/              # Smoke tests / local runners
├── tests/                # Pytest suite
├── docs/                 # System specs and planning
└── requirements.txt      # Python dependencies
```

### Module Breakdown

**backend/**
- `main.py` - FastAPI app initialization
- `config.py` - Environment-based settings
- `routes/` - API endpoints (health, demo, signals)

**mwt/**
- `models.py` - Pydantic models (MWTTrade, ConvictionSignal, WalletProfile)
- `normalizer.py` - Trade validation and normalization
- `listeners/` - Platform listener stubs (Hyperliquid, Jupiter, Ostium)

**conviction/**
- `engine.py` - Signal clustering and generation
- `scoring.py` - Conviction score calculations

**market/**
- `bias.py` - Market directional bias (stub)
- `structure.py` - Technical structure analysis (stub)
- `liquidations.py` - Liquidation cluster detection (stub)

**storage/**
- `db.py` - SQLite database wrapper
- `schema.sql` - Database schema

**paper/**
- `portfolio.py` - Paper portfolio management
- `simulator.py` - Paper trade execution from signals

**scripts/**
- `smoke_test.py` - End-to-end functionality test

**tests/**
- `test_normalizer.py` - Normalizer validation tests
- `test_conviction.py` - Conviction engine tests
- `test_paper.py` - Paper trading tests

**docs/**
- `MWT_SYSTEM_SPEC.md` - Complete architecture and design

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
python -m backend.main
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health & Status
```bash
GET /health          # System status
```

#### Demo & Signals
```bash
GET /demo/signal     # Generate demo SOL LONG conviction signal
GET /signals/        # List current signals
POST /signals/demo-paper  # Trade demo signal with paper simulator
```

## Testing

### Smoke Test

```bash
python scripts/smoke_test.py
```

Tests:
- Trade normalization
- Conviction signal generation
- Paper portfolio operations

### Unit Tests

```bash
pytest tests/
```

Coverage:
- Normalizer validation and asset filtering
- Conviction scoring and clustering
- Paper trading portfolio management

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# Application
APP_NAME=Oracle MWT Trader
PHASE=observe_only
LIVE_EXECUTION=false

# Server
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
LOG_LEVEL=INFO

# Conviction Engine
CONVICTION_THRESHOLD=0.75
WINDOW_MINUTES=15
MIN_CLUSTER_SIZE=2

# Paper Trading
STARTING_BALANCE=100000
DAILY_PROFIT_CAP=10000

# Active Assets (Phase 1 only)
ACTIVE_ASSETS=SOL,BTC,ETH,HYPE
```

## Development

This project is in **Phase 1** (visibility & normalization). Live trading execution is planned for future phases.

### Key Constraints

- ✋ No live trading
- ✋ No real API keys
- ✋ No wallet private keys or seeds
- ✋ No exchange secrets or funded credentials
- ✅ Mock data for development and testing
- ✅ Paper trading simulation for backtesting

### Example Workflow

1. **Ingest Mock Trades**
   ```python
   from mwt.normalizer import normalize_raw_trade
   
   raw = {
       "wallet_id": "whale_1",
       "asset": "SOL",
       "side": "long",
       "leverage": 20.0,
       "size_usd": 100000,
       "entry_price": 100.0,
       "platform": "ostium"
   }
   
   trade = normalize_raw_trade(raw)
   ```

2. **Build Conviction Signals**
   ```python
   from conviction.engine import ConvictionEngine
   
   engine = ConvictionEngine(min_score=0.75)
   engine.add_trade(trade)
   signals = engine.build_signals()
   ```

3. **Simulate Paper Trade**
   ```python
   from paper.simulator import PaperSimulator
   
   simulator = PaperSimulator()
   result = simulator.trade_signal(signals[0])
   ```

## Documentation

- [System Specification](docs/MWT_SYSTEM_SPEC.md) - Architecture, models, and design decisions

## Contributing

- Keep Phase 1 observation-only and paper-trading only
- Add tests for new features
- Update documentation when adding modules
- No real credentials or keys in code

## License

Proprietary - Oracle MWT Trader

## Contact

For questions or contributions, open an issue.
