"""
Tests for Conviction Engine
"""

import pytest
from conviction.engine import ConvictionEngine
from conviction.scoring import wallet_score, leverage_factor, recency_factor, trade_weight
from mwt.models import WalletProfile, MWTTrade, Asset, Side, Platform, WalletClass
from datetime import datetime, timedelta


def test_wallet_score():
    """Test wallet scoring"""
    profile = WalletProfile(
        wallet_id="test",
        winrate=0.6,
        avg_rr=2.0,
        consistency=0.7,
    )
    
    score = wallet_score(profile)
    assert 0 <= score <= 1
    # 0.6*0.5 + (2/5)*0.3 + 0.7*0.2 = 0.3 + 0.12 + 0.14 = 0.56
    assert 0.55 < score < 0.57


def test_leverage_factor():
    """Test leverage normalization"""
    assert leverage_factor(1.0) < leverage_factor(100.0)
    assert leverage_factor(200.0) == 1.0
    assert 0 <= leverage_factor(50.0) <= 1


def test_recency_factor():
    """Test recency decay"""
    now = datetime.utcnow()
    
    fresh = recency_factor(now, now, 15)
    assert fresh == 1.0
    
    old = recency_factor(now - timedelta(minutes=15), now, 15)
    assert old == 0.0
    
    mid = recency_factor(now - timedelta(minutes=7.5), now, 15)
    assert 0.45 < mid < 0.55


def test_conviction_engine_demo_signal():
    """Test conviction engine generates demo signal"""
    engine = ConvictionEngine(min_score=0.75, window_minutes=15)
    
    # Add demo trades
    for raw_data, profile in ConvictionEngine.demo_trades():
        from mwt.normalizer import normalize_raw_trade
        trade = normalize_raw_trade(raw_data)
        engine.add_trade(trade, profile)
    
    # Build signals
    signals = engine.build_signals()
    
    assert len(signals) > 0
    
    signal = signals[0]
    assert signal.asset == Asset.SOL
    assert signal.direction == Side.LONG
    assert signal.wallet_count >= 2
    assert 0 <= signal.conviction_score <= 1
    assert signal.conviction_score >= 0.75
