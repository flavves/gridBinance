
from binance.client import Client
from binance.enums import *
import DBManager
class BinanceTrader:
    def __init__(self, api_key, api_secret,db_file_path):
        self.client = Client(api_key, api_secret)
        self.db_manager = DBManager.DBManager(db_file_path)
    def place_order(self, symbol, side, order_type, quantity, price=None):
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


            return order
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def buy(self, symbol, order_type, quantity, price=None):
        """
        Place a buy order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Quantity to buy
        :param price: Price for limit orders
        :return: Order response
        """
        return self.place_order(symbol, SIDE_BUY, order_type, quantity, price)

    def sell(self, symbol, order_type, quantity, price=None):
        """
        Place a sell order on Binance.

        :param symbol: Trading pair symbol (e.g., 'BTCUSDT')
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Quantity to sell
        :param price: Price for limit orders
        :return: Order response
        """
        return self.place_order(symbol, SIDE_SELL, order_type, quantity, price)

