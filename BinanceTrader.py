from binance.client import Client
from binance.enums import *
import TelegramMessageSender
import logging  # Added logging import
import DBManager
class BinanceTrader:
    def __init__(self, api_key, api_secret, db_file_path, telegram_bot_token, telegram_chat_id):
        self.client = Client(api_key, api_secret)
        self.telegram_sender = TelegramMessageSender.TelegramMessageSender(telegram_bot_token, telegram_chat_id)
        self.dbFilePath = db_file_path
        
    def place_order(self, symbol, side, order_type, quantity, price=None, test=False, isBulk=False):
        """
        Place an order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Quantity to buy or sell
        :param price: Price for limit orders
        :return: Order response
        """
        
        try:
            if test == False:
                if order_type == 'LIMIT':
                    if price is None:
                        raise ValueError("Price must be specified for limit orders")
                    order = self.client.create_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=quantity,
                        price=price
                    )
                elif order_type == 'MARKET':
                    order = self.client.create_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity
                    )
                else:
                    raise ValueError("Invalid order type")
            else:
                logging.info("Test order")
                if order_type == 'LIMIT':
                    if price is None:
                        raise ValueError("Price must be specified for limit orders")
                    order = self.client.create_test_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=quantity,
                        price=price
                    )
                elif order_type == 'MARKET':
                    logging.info("Test order MARKET")
                    order = self.client.create_test_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity
                    )
                    logging.info(f"Test order MARKET: {order}")
                else:
                    raise ValueError("Invalid order type")

            trade_type = 'buy' if side == SIDE_BUY else 'sell'
            # Eger toplu alim degilse db ye ekle toplu alimlar db ye eklenmez
            if isBulk == False:
                db_manager = DBManager.DBManager(self.dbFilePath)
                result=db_manager.add_trade(symbol, trade_type, str(price), str(quantity), order['orderId'])
                try:
                    if result==1:
                        logging.info("data was added succesfuly to db")
                        pass
                    else:
                        logging.error("binancetrader dbmanager added error.")
                        return None
                except:
                    logging.error("Cannot add data to db!! Check Order!")
                    

            # Send a message to Telegram
            message = f"⌛️⌛️ Binance Trader => Emir verildi: {trade_type.upper()} {quantity} {symbol} Fiyat {price if price else 'market price'}"
            self.telegram_sender.send_message(message)
            logging.info(message)

            return order
        except Exception as e:
            error_message = f"Binance Trader => Alım satım kısmında hata olustu 🧨🧨🧨 {e}"
            logging.error(error_message)
            self.telegram_sender.send_message(error_message)
            return None

    def buy(self, symbol, order_type, quantity, price=None, test=False, isBulk=False):
        """
        Place a buy order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Quantity to buy
        :param price: Price for limit orders
        :return: Order response
        """
        return self.place_order(symbol, SIDE_BUY, order_type, quantity, price, test, isBulk)

    def sell(self, symbol, order_type, quantity, price=None, test=False):
        """
        Place a sell order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Quantity to sell
        :param price: Price for limit orders
        :return: Order response
        """
        return self.place_order(symbol, SIDE_SELL, order_type, quantity, price, test)

    def get_usdt_balance(self):
        """
        Returns the USDT balance in the Binance account.

        :return: USDT balance
        """
        try:
            balance = self.client.get_asset_balance(asset='USDT')
            return float(balance['free'])
        except Exception as e:
            error_message = f"Hesaptaki usdt miktarı alınıken hata olustu 🧨: {e}"
            logging.error(error_message)
            self.telegram_sender.send_message(error_message)
            return -1

    def get_coin_balance(self, symbol):
        """
        Returns the balance of the specified cryptocurrency.

        :param symbol: Cryptocurrency symbol (e.g., 'BTC')
        :return: Coin balance
        """
        try:
            balance = self.client.get_asset_balance(asset=symbol)
            return float(balance['free'])
        except Exception as e:
            error_message = f"Hesapta kaç adet olduğu sorgulanırken hata olustu {symbol} 🧨🧨: {e}"
            logging.error(error_message)
            self.telegram_sender.send_message(error_message)
            return None

    def get_current_price(self, symbol):
        """
        Returns the current price of the specified trading pair.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :return: Current price
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            error_message = f"🧨🧨 Fiyat çekilirken hata oluştu {symbol}: {e}"
            logging.error(error_message)
            self.telegram_sender.send_message(error_message)
            return None

    def check_order_status(self, symbol, order_id):
        """
        Check the status of an order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param order_id: ID of the order to check
        :return: Order status
        """
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order['status']
        except Exception as e:
            error_message = f"🧨 Emir sorgulanırken hata oluştu : {e}"
            logging.error(error_message)
            self.telegram_sender.send_message(error_message)
            return None

"""
from dotenv import load_dotenv
import os
load_dotenv()
if __name__ == "__main__":
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_API_SECRET')
    home_dir = os.path.expanduser('~')
    DB_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'trades.json')
    DB_OUTPUT_FILE_PATH=os.path.join(home_dir, 'python', 'gridBinance', 'current_prices.json')
    EXCELL_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'files', 'grid.xlsx')
    STATE_FILE = os.path.join(home_dir, 'python', 'gridBinance', 'botStates.json')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    trader = BinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    # Example usage
    usdt_balance = trader.get_usdt_balance()
    print(f"USDT Balance: {usdt_balance}")

    #get order status
    symbol = 'DOGEUSDT'
    order_id = 9025075837
    order_status = trader.check_order_status(symbol, order_id)
    print(f"Order status: {order_status}")

    #PLACE A ORDER
    symbol = 'DOGEUSDT'
    side = 'BUY'
    order_type = 'LIMIT'
    quantity = 100
    price = 0.2
    test = False
    isBulk = False
    order = trader.place_order(symbol, side, order_type, quantity, price, test, isBulk)
    print(order)
"""