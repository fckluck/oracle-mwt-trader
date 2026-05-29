"""
Tests for MWT Normalizer
"""

import pytest
from mwt.normalizer import normalize_raw_trade, validate_asset
from mwt.models import Asset, WalletClass


def test_normalize_valid_sol_long():
    """Test normalizing valid SOL long trade"""
    raw = {
        "wallet_id": "whale_1",
        "wallet_class": WalletClass.WHALE.value,
        "asset": "SOL",
        "side": "long",
        "leverage": 20.0,
        "size_usd": 100000,
        "entry_price": 100.0,
        "platform": "ostium",
    }
    
    trade = normalize_raw_trade(raw)
    
    assert trade.asset == Asset.SOL
    assert trade.side.value == "long"
    assert trade.leverage == 20.0
    assert trade.size_usd == 100000


def test_reject_unsupported_asset():
    """Test rejecting unsupported asset"""
    raw = {
        "wallet_id": "test",
        "asset": "XRP",  # Not in Phase 1
        "side": "long",
        "leverage": 1.0,
        "size_usd": 1000,
        "entry_price": 1.0,
        "platform": "unknown",
    }
    
    with pytest.raises(ValueError, match="not supported"):
        normalize_raw_trade(raw)


def test_reject_invalid_leverage():
    """Test rejecting invalid leverage"""
    raw = {
        "wallet_id": "test",
        "asset": "BTC",
        "side": "long",
        "leverage": 500.0,  # Too high
        "size_usd": 1000,
        "entry_price": 1.0,
        "platform": "unknown",
    }
    
    with pytest.raises(ValueError, match="Leverage"):
        normalize_raw_trade(raw)


def test_validate_asset():
    """Test asset validation"""
    asset = validate_asset("SOL")
    assert asset == Asset.SOL
    
    with pytest.raises(ValueError):
        validate_asset("XRP")
