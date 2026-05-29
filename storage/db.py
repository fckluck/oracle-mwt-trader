"""
Database Layer

SQLite persistence for trades, signals, and positions.
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Database:
    """SQLite database wrapper"""
    
    def __init__(self, path: str = "oracle_mwt.db"):
        """Initialize database
        
        Args:
            path: Database file path
        """
        self.path = path
        self.init_db()
    
    def init_db(self) -> None:
        """Initialize database schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            logger.warning(f"Schema file not found: {schema_path}")
            return
        
        with open(schema_path) as f:
            schema = f.read()
        
        conn = sqlite3.connect(self.path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.path}")
    
    def insert_mwt_trade(self, trade_dict: Dict) -> int:
        """Insert MWT trade
        
        Args:
            trade_dict: Trade data
            
        Returns:
            Trade ID
        """
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO mwt_trades
            (wallet_id, wallet_class, asset, side, leverage, size_usd, entry_price, platform, timestamp, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trade_dict.get("wallet_id"),
                trade_dict.get("wallet_class", "unknown"),
                trade_dict.get("asset"),
                trade_dict.get("side"),
                trade_dict.get("leverage"),
                trade_dict.get("size_usd"),
                trade_dict.get("entry_price"),
                trade_dict.get("platform"),
                trade_dict.get("timestamp"),
                json.dumps(trade_dict.get("raw", {})),
            )
        )
        
        conn.commit()
        trade_id = cursor.lastrowid
        conn.close()
        
        return trade_id
    
    def insert_conviction_signal(self, signal_dict: Dict) -> int:
        """Insert conviction signal
        
        Args:
            signal_dict: Signal data
            
        Returns:
            Signal ID
        """
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO conviction_signals
            (asset, direction, total_size_usd, avg_entry, wallet_count, platforms, conviction_score, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal_dict.get("asset"),
                signal_dict.get("direction"),
                signal_dict.get("total_size_usd"),
                signal_dict.get("avg_entry"),
                signal_dict.get("wallet_count"),
                json.dumps(signal_dict.get("platforms", [])),
                signal_dict.get("conviction_score"),
                signal_dict.get("first_seen"),
                signal_dict.get("last_seen"),
            )
        )
        
        conn.commit()
        signal_id = cursor.lastrowid
        conn.close()
        
        return signal_id
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent conviction signals
        
        Args:
            limit: Max results
            
        Returns:
            List of signals
        """
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT * FROM conviction_signals
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
