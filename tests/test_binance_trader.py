import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from BinanceTrader import BinanceTrader
from unittest.mock import MagicMock

@pytest.fixture
def trader():
    api_key = "test_api_key"
    api_secret = "test_api_secret"
    db_file_path = "test_trades.json"
    telegram_bot_token = "test_telegram_bot_token"
    telegram_chat_id = "test_telegram_chat_id"
    trader = BinanceTrader(api_key, api_secret, db_file_path, telegram_bot_token, telegram_chat_id)
    trader.client.create_order = MagicMock(return_value={"status": "success"})
    trader.db_manager.add_trade = MagicMock(return_value="Trade added successfully")
    trader.telegram_sender.send_message = MagicMock(return_value="Message sent successfully")
    return trader

def test_buy_order(trader):
    response = trader.buy("BTCUSDT", "LIMIT", 0.001, 50000)
    assert response["status"] == "success"
    trader.db_manager.add_trade.assert_called_once()
    trader.telegram_sender.send_message.assert_called_once()

def test_sell_order(trader):
    response = trader.sell("BTCUSDT", "LIMIT", 0.001, 50000)
    assert response["status"] == "success"
    trader.db_manager.add_trade.assert_called_once()
    trader.telegram_sender.send_message.assert_called_once()