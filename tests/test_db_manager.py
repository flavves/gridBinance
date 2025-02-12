import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
import os
import json
from DBManager import DBManager

@pytest.fixture
def db_manager(tmp_path):
    db_file_path = tmp_path / "test_trades.json"
    return DBManager(db_file_path)

def test_add_trade(db_manager):
    response = db_manager.add_trade("BTCUSDT", "buy", 50000, 0.001)
    assert response == "Trade added successfully: buy 0.001 BTCUSDT at 50000"
    trades = db_manager.get_trades("BTCUSDT")
    assert len(trades["buyOrders"]) == 1

def test_get_trades(db_manager):
    db_manager.add_trade("BTCUSDT", "buy", 50000, 0.001)
    trades = db_manager.get_trades("BTCUSDT")
    assert len(trades["buyOrders"]) == 1
    assert trades["buyOrders"][0]["price"] == 50000
    assert trades["buyOrders"][0]["qty"] == 0.001