import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Proje dizinini sys.path'e ekleyerek modüllerin düzgün yüklenmesini sağlıyoruz.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BinanceTrader import BinanceTrader

@pytest.fixture
def trader():
    api_key = "test_api_key"
    api_secret = "test_api_secret"
    db_file_path = "test_trades.json"
    telegram_bot_token = "test_telegram_bot_token"
    telegram_chat_id = "test_telegram_chat_id"

    with patch("BinanceTrader.Client") as mock_client:
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_order = MagicMock(return_value={"status": "success"})
        
        trader = BinanceTrader(api_key, api_secret, db_file_path, telegram_bot_token, telegram_chat_id)
        trader.client = mock_client_instance
        
        # Diğer bağımlılıkları da mock'luyoruz
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

def test_get_usdt_balance(trader):
    trader.client.get_asset_balance = MagicMock(return_value={'free': '100.0'})
    balance = trader.get_usdt_balance()
    assert balance == 100.0

def test_get_coin_balance(trader):
    trader.client.get_asset_balance = MagicMock(return_value={'free': '50.0'})
    balance = trader.get_coin_balance('BTC')
    assert balance == 50.0
