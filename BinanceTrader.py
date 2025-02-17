
from binance.client import Client
from binance.enums import *
import DBManager
import TelegramMessageSender
class BinanceTrader:
    def __init__(self, api_key, api_secret, db_file_path, telegram_bot_token, telegram_chat_id):
        self.client = Client(api_key, api_secret)
        self.db_manager = DBManager.DBManager(db_file_path)
        self.telegram_sender = TelegramMessageSender.TelegramMessageSender(telegram_bot_token, telegram_chat_id)

    def place_order(self, symbol, side, order_type, quantity, price=None, test=False):
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
            if test==False:
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
            
            trade_type = 'buy' if side == SIDE_BUY else 'sell'
            self.db_manager.add_trade(symbol, trade_type, price, quantity)

            #   Send a message to Telegram
            message = f"Order placed: {trade_type.upper()} {quantity} {symbol} at {price if price else 'market price'}"
            self.telegram_sender.send_message(message)

            return order
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            self.telegram_sender.send_message(error_message)
            return None

    def buy(self, symbol, order_type, quantity, price=None, test=False):
        """
        Place a buy order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Quantity to buy
        :param price: Price for limit orders
        :return: Order response
        """
        return self.place_order(symbol, SIDE_BUY, order_type, quantity, price, test)

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
            error_message = f"An error occurred while retrieving USDT balance: {e}"
            print(error_message)
            self.telegram_sender.send_message(error_message)
            return None

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
            error_message = f"An error occurred while retrieving {symbol} balance: {e}"
            print(error_message)
            self.telegram_sender.send_message(error_message)
            return None