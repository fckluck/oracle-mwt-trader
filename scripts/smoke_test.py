#!/usr/bin/env python
"""
Smoke Test

Tests core functionality:
- Normalizer
- Conviction engine
- Paper trading
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mwt.normalizer import normalize_raw_trade
from conviction.engine import ConvictionEngine
from paper.portfolio import PaperPortfolio
from mwt.models import WalletClass
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


def test_normalizer():
    """Test trade normalization"""
    logger.info("\n=== Test: Normalizer ===")
    
    raw_trade = {
        "wallet_id": "test_wallet",
        "wallet_class": WalletClass.WHALE.value,
        "asset": "SOL",
        "side": "long",
        "leverage": 20.0,
        "size_usd": 100000,
        "entry_price": 100.0,
        "platform": "ostium",
    }
    
    trade = normalize_raw_trade(raw_trade)
    logger.info(f"✅ Normalized trade: {trade.asset} {trade.side} @ {trade.entry_price}")
    assert trade.asset.value == "SOL"
    assert trade.side.value == "long"
    return True


def test_conviction():
    """Test conviction engine"""
    logger.info("\n=== Test: Conviction Engine ===")
    
    engine = ConvictionEngine(min_score=0.75, window_minutes=15)
    
    # Add demo trades
    for raw_data, profile in ConvictionEngine.demo_trades():
        trade = normalize_raw_trade(raw_data)
        engine.add_trade(trade, profile)
    
    # Build signals
    signals = engine.build_signals()
    
    logger.info(f"✅ Generated {len(signals)} signal(s)")
    if signals:
        sig = signals[0]
        logger.info(f"  - {sig.asset.value} {sig.direction.value} ")
        logger.info(f"    Conviction: {sig.conviction_score:.2f}")
        logger.info(f"    Size: ${sig.total_size_usd:,.0f}")
        logger.info(f"    Wallets: {sig.wallet_count}")
    
    assert len(signals) > 0
    return True


def test_paper_trading():
    """Test paper portfolio"""
    logger.info("\n=== Test: Paper Trading ===")
    
    portfolio = PaperPortfolio(
        starting_balance=100000.0,
        daily_profit_cap=10000.0,
    )
    
    # Open position
    pos = portfolio.open_probe(
        asset="SOL",
        side="long",
        leverage=5.0,
        size_usd=5000.0,
        entry_price=100.0,
    )
    
    logger.info(f"✅ Opened probe: {pos.position_id}")
    logger.info(f"  - Size: ${pos.size_usd}")
    logger.info(f"  - Entry: {pos.entry_price}")
    
    # Close position (simulate 2% profit)
    exit_price = 102.0
    result = portfolio.close_position(pos.position_id, exit_price)
    
    logger.info(f"✅ Closed position")
    logger.info(f"  - P&L: ${result['pnl_usd']:+.2f} ({result['pnl_pct']:+.2f}%)")
    logger.info(f"  - Balance: ${portfolio.get_balance():,.2f}")
    
    assert result["pnl_usd"] > 0
    return True


def main():
    """Run all tests"""
    logger.info("🚀 Oracle MWT Trader - Smoke Test")
    logger.info("=" * 50)
    
    tests = [
        ("Normalizer", test_normalizer),
        ("Conviction", test_conviction),
        ("Paper Trading", test_paper_trading),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
            failed += 1
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
