-- Oracle MWT Trader Phase 1 Schema
-- SQLite database for trades, signals, and paper trading

CREATE TABLE IF NOT EXISTS wallet_profiles (
    wallet_id TEXT PRIMARY KEY,
    winrate REAL DEFAULT 0.5,
    avg_rr REAL DEFAULT 1.0,
    consistency REAL DEFAULT 0.5,
    wallet_class TEXT DEFAULT 'unknown',
    trades_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mwt_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id TEXT NOT NULL,
    wallet_class TEXT DEFAULT 'unknown',
    asset TEXT NOT NULL,
    side TEXT NOT NULL,
    leverage REAL NOT NULL,
    size_usd REAL NOT NULL,
    entry_price REAL NOT NULL,
    platform TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    raw_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(wallet_id) REFERENCES wallet_profiles(wallet_id)
);

CREATE TABLE IF NOT EXISTS conviction_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset TEXT NOT NULL,
    direction TEXT NOT NULL,
    total_size_usd REAL NOT NULL,
    avg_entry REAL NOT NULL,
    wallet_count INTEGER NOT NULL,
    platforms TEXT,
    conviction_score REAL NOT NULL,
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    trade_ids TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paper_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT UNIQUE NOT NULL,
    asset TEXT NOT NULL,
    side TEXT NOT NULL,
    leverage REAL NOT NULL,
    size_usd REAL NOT NULL,
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_price REAL,
    exit_time TIMESTAMP,
    pnl_usd REAL DEFAULT 0.0,
    pnl_pct REAL DEFAULT 0.0,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paper_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(position_id) REFERENCES paper_positions(position_id)
);

CREATE INDEX IF NOT EXISTS idx_trades_asset ON mwt_trades(asset);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON mwt_trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_asset ON conviction_signals(asset);
CREATE INDEX IF NOT EXISTS idx_signals_created ON conviction_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_positions_status ON paper_positions(status);
