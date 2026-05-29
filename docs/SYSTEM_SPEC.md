# Oracle MWT Trader: System Specification

## 1. Overview

Oracle MWT Trader is a **Multi-Wallet Tracking (MWT)** system for perpetual futures markets. It observes smart money behavior across venues, detects directional conviction, and prepares hypothetical execution signals.

**Core Mission**: Track conviction, not execute orders.

## 2. Architecture

```
Event Ingestion (mwt/listeners)
         ↓
   Normalization (mwt/normalizer)
         ↓
   Conviction Engine (conviction/engine)
         ↓
   Storage (storage/*)
         ↓
   API Layer (backend/routes)
         ↓
   Paper Trading (paper/engine)
```

## 3. Key Concepts

### Multi-Wallet Tracking (MWT)

An MWT Object represents a normalized wallet trade event across any venue:

```python
class MWTEvent:
    timestamp: datetime        # When trade occurred
    wallet_address: str        # Wallet ID (anonymized if necessary)
    platform: str              # "hyperliquid", "dydx", "bitmex" (mock in Phase 1)
    asset: str                 # "SOL", "BTC", "ETH", "HYPE"
    side: Literal["long", "short"]
    notional_usd: float        # Trade size
    entry_price: float         # Price at entry
    leverage: int              # 1x to 20x (or platform-specific)
    source: Literal["live", "mock"]
    confidence: float          # 0.0–1.0 (credibility)
```

### Conviction Cluster

Groups of MWT events forming a directional signal:

```python
class ConvictionCluster:
    asset: str
    direction: Literal["long", "short"]
    wallet_count: int          # Number of unique wallets
    total_notional: float      # Sum of all trades
    avg_leverage: float
    confidence: float          # Aggregated confidence
    events: List[MWTEvent]
    created_at: datetime
    invalidated_at: Optional[datetime]
```

### Invalidation Logic

Conviction breaks when:
1. **Liquidation cascade**: Multiple clustered wallets show liquidation-like behavior
2. **Direction reversal**: Cluster initiators reverse position
3. **Low conviction renewal**: No new high-confidence events after N minutes
4. **Volatility spike**: Asset price moves >X% against cluster direction

## 4. Phase 1 Components

### 4.1 Event Ingestion (mwt/listeners)

**Mock listener** simulates venue events with:
- Configurable event rate (trades/minute)
- Realistic asset distribution
- Wallet clustering (some wallets trade together)
- Leverage distribution
- Rare liquidation events

### 4.2 Normalizer (mwt/normalizer)

Converts platform-specific trade objects to MWTEvent:

```python
def normalize_event(raw_event) -> MWTEvent:
    # Extract common fields from different sources
    # Validate leverage, notional, and confidence
    # Return standardized MWT object
```

### 4.3 Conviction Engine (conviction/engine)

Clusters correlated MWT events:

```python
def compute_conviction(events: List[MWTEvent]) -> List[ConvictionCluster]:
    # 1. Group by asset and direction
    # 2. Detect wallet clusters (co-movement)
    # 3. Score confidence (size, leverage, source)
    # 4. Check invalidation conditions
    # 5. Return ranked clusters
```

### 4.4 Storage (storage/*)

- **events.py**: Event buffer (in-memory + optional file)
- **trades.py**: Trade history and metadata
- **conviction_state.py**: Current clusters and state
- **db.py**: Optional SQLite integration (Phase 1b)

### 4.5 API Routes (backend/routes)

#### GET /api/conviction/current
```json
{
  "top_conviction": {
    "asset": "SOL",
    "direction": "long",
    "score": 0.87,
    "wallet_count": 12,
    "notional_usd": 1250000
  },
  "timestamp": "2026-05-29T10:30:00Z"
}
```

#### GET /api/wallets
```json
{
  "wallets": [
    {
      "address": "wallet_1",
      "recent_assets": ["SOL", "ETH"],
      "recent_trades": 15,
      "last_trade": "2026-05-29T10:25:00Z"
    }
  ]
}
```

#### GET /api/health
```json
{
  "status": "healthy",
  "events_in_buffer": 342,
  "clusters_active": 3,
  "last_update": "2026-05-29T10:30:01Z"
}
```

### 4.6 Paper Trading (paper/*)

- **portfolio.py**: Mock portfolio with initial cash
- **engine.py**: Simulate fills at market prices
- **history.py**: Track hypothetical P&L

## 5. Data Flow Example

```
1. Mock listener generates event:
   {wallet: "w123", asset: "SOL", side: "long", notional: 100k, leverage: 5}

2. Normalizer validates → MWTEvent object

3. Engine receives event → updates conviction clusters

4. Cluster threshold met → broadcasts signal

5. Paper engine simulates fill:
   - Current price: $180
   - Size: 100k / 180 = 556 SOL
   - Hypothetical hold time tracked

6. API returns conviction via /api/conviction/current
```

## 6. Security & Compliance

### Phase 1 Constraints

- **No real credentials**: All API keys are mock/dummy
- **No private keys**: Zero wallet signing capability
- **No autonomous execution**: Signals only, no order placement
- **No live funds**: Paper trading only
- **Git safety**: .gitignore blocks .env files with real secrets

### Credential Management

- `.env.example`: Template with dummy values
- `.env`: (ignored) Local config with real values (if needed later)
- `config.py`: Loads from `.env`, validates required fields

## 7. Deployment

### Local Development
```bash
pip install -r requirements.txt
python backend/main.py
```

### Docker
```bash
docker build -t oracle-mwt-trader .
docker run -p 8000:8000 oracle-mwt-trader
```

### Environment

```
FASTAPI_ENV=development
MWT_LISTEN_PORT=8000
MWT_EVENT_RATE=10       # events/min
MWT_CONVICTION_TTL=300  # seconds
```

## 8. Testing Strategy

### Unit Tests
- Normalizer correctness
- Conviction clustering logic
- Invalidation triggers
- Paper trading fills

### Integration Tests
- Full event → conviction → API flow
- Concurrent event ingestion
- Storage persistence

### Load Tests
- 1000 events/min throughput
- Conviction computation latency <100ms
- API response time <50ms

## 9. Future Phases

**Phase 2**: Live market data integration (Hyperliquid API, dYdX API)  
**Phase 3**: Real-time invalidation via websockets  
**Phase 4**: Paper-trade execution engine  
**Phase 5**: Production-ready execution (gated, audited, permissioned)

---

**Philosophy**: The bot does not fear being wrong. It fears not recognizing invalidation fast enough.
