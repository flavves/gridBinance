import os
import BinanceTrader

LIMIT="LIMIT"
MARKET="MARKET"

# Example usage
if __name__ == "__main__":
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_API_SECRET')
    home_dir = os.path.expanduser('~')
    DB_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'trades.json')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    trader = BinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    symbol = 'BTCUSDT'
    order_type = 'LIMIT'
    quantity = 0.001
    price = 50000

    # Place a buy order
    buy_order = trader.buy(symbol, order_type, quantity, price)
    print("Buy order response:", buy_order)

    # Place a sell order
    sell_order = trader.sell(symbol, order_type, quantity, price)
    print("Sell order response:", sell_order)