"""
Tests for Paper Trading
"""

import pytest
from paper.portfolio import PaperPortfolio
from paper.simulator import PaperSimulator
from conviction.engine import ConvictionEngine
from mwt.normalizer import normalize_raw_trade


def test_portfolio_can_trade():
    """Test portfolio trade limit"""
    portfolio = PaperPortfolio(
        starting_balance=100000.0,
        daily_profit_cap=100.0,  # Very low
    )
    
    assert portfolio.can_trade() is True
    
    portfolio.realized_pnl = 100.0
    assert portfolio.can_trade() is False


def test_portfolio_open_close():
    """Test opening and closing positions"""
    portfolio = PaperPortfolio(starting_balance=100000.0)
    
    # Open position
    pos = portfolio.open_probe(
        asset="SOL",
        side="long",
        leverage=5.0,
        size_usd=1000.0,
        entry_price=100.0,
    )
    
    assert pos is not None
    assert len(portfolio.open_positions) == 1
    
    # Close with profit
    result = portfolio.close_position(pos.position_id, 102.0)
    
    assert result["pnl_usd"] > 0
    assert len(portfolio.open_positions) == 0
    assert len(portfolio.closed_positions) == 1


def test_simulator_trade_signal():
    """Test simulator trades signal"""
    engine = ConvictionEngine(min_score=0.75, window_minutes=15)
    
    # Add demo trades
    for raw_data, profile in ConvictionEngine.demo_trades():
        trade = normalize_raw_trade(raw_data)
        engine.add_trade(trade, profile)
    
    signals = engine.build_signals()
    assert len(signals) > 0
    
    simulator = PaperSimulator()
    result = simulator.trade_signal(signals[0])
    
    assert result["status"] == "opened"
    assert "position_id" in result
