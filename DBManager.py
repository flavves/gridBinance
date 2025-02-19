import json
import os

class DBManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}

    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)
            return True

    def add_trade(self, coin, trade_type, price, qty, order_id):
        if coin not in self.data:
            self.data[coin] = {'buyOrders': [], 'sellOrders': []}
        if trade_type == 'buy':
            if any(trade['price'] == price for trade in self.data[coin]['buyOrders']):
                return f"Error: Trade with price {price} already exists in buy orders."
            self.data[coin]['buyOrders'].append({
                'price': price,
                'qty': qty,
                'orderId': order_id
            })
        elif trade_type == 'sell':
            if any(trade['price'] == price for trade in self.data[coin]['sellOrders']):
                return f"Error: Trade with price {price} already exists in sell orders."
            self.data[coin]['sellOrders'].append({
                'price': price,
                'qty': qty,
                'orderId': order_id
            })
        self.save_data()
        return f"Trade added successfully: {trade_type} {qty} {coin} at {price}"

    def update_trade(self, coin, trade_type, index, price=None, qty=None):
        if coin in self.data and trade_type in ['buyOrders', 'sellOrders'] and 0 <= index < len(self.data[coin][trade_type]):
            if price is not None:
                self.data[coin][trade_type][index]['price'] = price
            if qty is not None:
                self.data[coin][trade_type][index]['qty'] = qty
            self.save_data()
            return f"Trade updated successfully."
        return f"Error: Coin {coin} or trade type {trade_type} not found."

    def delete_trade(self, coin, trade_type, price):
        if coin in self.data and trade_type in ['buyOrders', 'sellOrders']:
            self.data[coin][trade_type] = [trade for trade in self.data[coin][trade_type] if trade['price'] != price]
            self.save_data()
            return f"Trade with price {price} deleted successfully."
        return f"Error: Coin {coin} or trade type {trade_type} not found."

    def get_trades(self, coin):
        return self.data.get(coin, {'buyOrders': [], 'sellOrders': []})


    def isTradeExists(self, coin, trade_type, price):
        if coin in self.data and trade_type in ['buyOrders', 'sellOrders']:
            return any(trade['price'] == price for trade in self.data[coin][trade_type])
        return False


"""
# Usage example
if __name__ == "__main__":
    db_manager = DBManager('/home/batuhanokmen/python/gridBinance/trades.json')
    print(db_manager.add_trade('ADAUSDT', 'buy', 0.70, 10))
    print(db_manager.add_trade('ADAUSDT', 'buy', 0.71, 10))
    print(db_manager.add_trade('ADAUSDT', 'sell', 0.79, 9))
    print(db_manager.add_trade('ADAUSDT', 'sell', 0.80, 9))
    print(db_manager.add_trade('CAKEUSDT', 'buy', 2.22, 10))
    print(db_manager.add_trade('CAKEUSDT', 'sell', 2.96, 10))
    #db_manager.update_trade('ETHUSDT', 'sellOrders', 0, price=3020)
    #print(db_manager.get_trades('ETHUSDT'))
    #db_manager.delete_trade('ETHUSDT', 'buyOrders', 3000)
    #print(db_manager.get_trades('ETHUSDT'))
"""