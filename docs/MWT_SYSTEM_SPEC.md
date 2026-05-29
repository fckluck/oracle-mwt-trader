# Oracle MWT Trader - Phase 1 System Specification

## Overview

**Oracle MWT Trader** is a multi-platform smart money tracking system for perpetual futures markets.

**Phase 1** is **observe-only** and **paper-trading only**. No live order execution.

### Core Concepts

**MWT (Multi-Wallet Tracking):**
- Aggregates wallet trading activity from multiple platforms
- Normalizes into unified objects
- Clusters by asset, side, and time window
- Emits conviction signals indicating smart money alignment

**Conviction Score:**
- Measures signal strength (0.0 to 1.0)
- Factors: wallet profile (40%), position size (30%), leverage (20%), recency (10%)
- Weighted average of coordinated trades

**Wallet Classification:**
- **WHALE**: High winrate, strong consistency (>$500k typically)
- **ACTIVE_TRADER**: Regular trader, moderate stats
- **UNKNOWN**: Unclassified

### Supported Platforms (Phase 1)

- Hyperliquid (perp)
- Jupiter (swap)
- Ostium (OTC)
- Apex (coming)

### Active Assets (Phase 1)

- **SOL** - Solana
- **BTC** - Bitcoin
- **ETH** - Ethereum
- **HYPE** - Hype (alt)

*Future assets (Phase 2+): XRP, BNB, ADA*

## System Architecture

```
┌─────────────────────────────────┐
│   Platform Listeners (Stub)     │
│  Hyperliquid, Jupiter, Ostium   │
└──────────────┬──────────────────┘
               │ Raw Trade Data
               ▼
┌──────────────────────────────────┐
│   MWT Normalizer                 │
│  Validates & Normalizes Trades   │
└──────────────┬───────────────────┘
               │ MWTTrade Objects
               ▼
┌──────────────────────────────────┐
│   Conviction Engine              │
│  Clusters & Scores Signals       │
└──────────────┬───────────────────┘
               │ ConvictionSignal
               ▼
┌──────────────────────────────────┐
│   Paper Simulator                │
│  Opens Probe Positions           │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   SQLite Storage                 │
│  Trades, Signals, Positions      │
└──────────────────────────────────┘
```

## Data Models

### MWTTrade

Normalized wallet trading activity.

```python
class MWTTrade:
    wallet_id: str
    wallet_class: WalletClass
    asset: Asset  # SOL, BTC, ETH, HYPE
    side: Side    # LONG, SHORT
    leverage: float
    size_usd: float
    entry_price: float
    platform: Platform
    timestamp: datetime
    raw: dict
```

### ConvictionSignal

Aggregated smart money activity signal.

```python
class ConvictionSignal:
    asset: Asset
    direction: Side
    total_size_usd: float
    avg_entry: float
    wallet_count: int
    platforms: List[str]
    conviction_score: float  # 0-1, higher = stronger
    first_seen: datetime
    last_seen: datetime
    trades: List[MWTTrade]
```

## Conviction Scoring

### Wallet Score

```
walelt_score = winrate * 0.5 + avg_rr_normalized * 0.3 + consistency * 0.2
```

Range: 0.0 to 1.0

### Trade Weight

```
trade_weight = wallet_score * 0.4 + log_size_factor * 0.3 + leverage_factor * 0.2 + recency_factor * 0.1
```

### Signal Conviction

```
conviction_score = avg(all_trade_weights_in_cluster)
```

Minimum for signal: 0.75 (configurable)

## API Endpoints

### Health

```bash
GET /health
```

Returns system status.

### Demo

```bash
GET /demo/signal
```

Generates demo whale + trader SOL LONG signal.

### Signals

```bash
GET /signals/
POST /signals/demo-paper
```

List signals or trade demo signal with paper simulator.

## Configuration

```env
# Conviction
CONVICTION_THRESHOLD=0.75       # Min conviction to emit signal
WINDOW_MINUTES=15                 # Clustering time window

# Paper Trading
STARTING_BALANCE=100000
DAILY_PROFIT_CAP=10000

# Active Assets
ACTIVE_ASSETS=SOL,BTC,ETH,HYPE
```

## Phase 1 Constraints

✋ **No Live Execution**
- No real order placement
- No exchange APIs
- No private key handling
- No signing or transactions

✋ **No Private Keys or Secrets**
- No wallet credentials
- No API keys in code
- All environment-based

✅ **Observation Only**
- Track smart money
- Detect conviction
- Paper simulate trades
- Analyze results

## Testing

### Smoke Test

```bash
python scripts/smoke_test.py
```

Tests:
- Normalizer (valid SOL trade)
- Conviction (demo signal generation)
- Paper trading (open/close positions)

### Unit Tests

```bash
pytest tests/
```

Tests coverage:
- Normalizer validation
- Conviction scoring
- Paper portfolio

## Development

### Add New Asset (Phase 2)

1. Add to `Asset` enum in `mwt/models.py`
2. Add to `ALLOWED_ASSETS` in `mwt/normalizer.py`
3. Update `ACTIVE_ASSETS` in `backend/config.py`
4. Add listener stub in `mwt/listeners/`

### Add New Platform (Phase 2)

1. Add to `Platform` enum in `mwt/models.py`
2. Create `mwt/listeners/platform_name.py`
3. Implement `listen_platform_name()` function

### Add Market Analysis (Phase 2)

1. Enhance `market/bias.py` with real bias detection
2. Enhance `market/structure.py` with technical analysis
3. Integrate into conviction scoring

## Future Phases

### Phase 2: Smart Execution
- Entry order construction
- Risk management
- Position sizing
- Dry-run execution

### Phase 3: Live Trading
- Real exchange connections
- Signed transactions
- Position tracking
- P&L monitoring

### Phase 4: Advanced Analysis
- Multi-asset correlation
- Sentiment scoring
- On-chain metrics
- ML-based models

## Philosophy

> The bot does not fear being wrong. It fears not recognizing invalidation fast enough.

**Aggressive observation, conservative execution.**

- Detect signals early and broadly
- Validate before trading
- Exit fast on invalidation
- Learn from every trade
