import json
import os
import logging

class DBManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()
        #logging.info(f"DBManager initialized with file: {self.file_path}")

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as file:
                    #logging.info(f"Loading data from {self.file_path}")
                    return json.load(file)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {self.file_path}: {e}")
                return {}
        else:
            logging.warning(f"File {self.file_path} not found. Initializing empty database.")
            return {}

    def save_data(self):
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file, indent=4)
            logging.info(f"Data successfully saved to {self.file_path}")
            file.close()
            return True
        except Exception as e:
            logging.error(f"Error saving data to {self.file_path}: {e}")
            return False

    def add_trade(self, coin, trade_type, price, qty, order_id):
        logging.info(f"Adding trade - Coin: {coin}, Type: {trade_type}, Price: {price}, Qty: {qty}, Order ID: {order_id}")
        
        if coin not in self.data:
            self.data[coin] = {'buyOrders': [], 'sellOrders': []}
        
        trade_list = self.data[coin]['buyOrders'] if trade_type == 'buy' else self.data[coin]['sellOrders']
        
        if any(trade['price'] == price for trade in trade_list):
            logging.warning(f"Trade with price {price} already exists in {trade_type} orders for {coin}.")
            return f"Error: Trade with price {price} already exists in {trade_type} orders."

        trade_list.append({
            'price': price,
            'qty': qty,
            'orderId': order_id
        })

        if self.save_data():
            logging.info(f"Trade added successfully: {trade_type} {qty} {coin} at {price}")
            return 1
        return "Error: Failed to save trade."

    def update_trade(self, coin, trade_type, index, price=None, qty=None):
        logging.info(f"Updating trade - Coin: {coin}, Type: {trade_type}, Index: {index}, Price: {price}, Qty: {qty}")

        if coin in self.data and trade_type in ['buyOrders', 'sellOrders']:
            if 0 <= index < len(self.data[coin][trade_type]):
                if price is not None:
                    self.data[coin][trade_type][index]['price'] = price
                if qty is not None:
                    self.data[coin][trade_type][index]['qty'] = qty

                if self.save_data():
                    return f"Trade updated successfully."
                return "Error: Failed to save updated trade."

        logging.error(f"Error: Coin {coin} or trade type {trade_type} not found.")
        return f"Error: Coin {coin} or trade type {trade_type} not found."
 
    def delete_trade(self, coin, trade_type, order_id):
        logging.info(f"Deleting trade - Coin: {coin}, Type: {trade_type}, Order ID: {order_id}")

        if coin in self.data and trade_type in ['buyOrders', 'sellOrders']:
            initial_length = len(self.data[coin][trade_type])
            self.data[coin][trade_type] = [trade for trade in self.data[coin][trade_type] if trade['orderId'] != order_id]
            
            if len(self.data[coin][trade_type]) < initial_length:
                if self.save_data():
                    logging.info(f"Trade with Order ID {order_id} deleted successfully from {trade_type} orders of {coin}.")
                    return f"Trade with Order ID {order_id} deleted successfully."
            else:
                logging.warning(f"Trade with Order ID {order_id} not found in {trade_type} orders for {coin}.")
                return f"Error: Trade with Order ID {order_id} not found."

        logging.error(f"Error: Coin {coin} or trade type {trade_type} not found.")
        return f"Error: Coin {coin} or trade type {trade_type} not found."
    
    
    def get_trades(self, coin):
        logging.info(f"Fetching trades for {coin}.")
        return self.data.get(coin, {'buyOrders': [], 'sellOrders': []})
    
    def get_all_trades(self):
            return self.data
        
    def isTradeExists(self, coin, trade_type, price):
        logging.info(f"Checking if trade exists - Coin: {coin}, Type: {trade_type}, Price: {price}")

        if coin in self.data and trade_type in ['buyOrders', 'sellOrders']:
            exists = any(trade['price'] == price for trade in self.data[coin][trade_type])
            if exists:
                logging.info(f"Trade with price {price} found in {trade_type} orders for {coin}.")
            else:
                logging.info(f"Trade with price {price} NOT found in {trade_type} orders for {coin}.")
            return exists

        logging.error(f"Error: Coin {coin} or trade type {trade_type} not found.")
        return False


# Usage example (uncomment to test)
"""
if __name__ == "__main__":
    symbol="DOGEUSDT"
    db_manager = DBManager('/root/gridBinance/trades copy.json')
    print(db_manager.get_trades(symbol))
    print(db_manager.get_all_trades())
    trades=db_manager.get_all_trades()
    buy_orders = trades[symbol].get("buyOrders", [])
    sell_orders = trades[symbol].get("sellOrders", [])
    db_manager.delete_trade(symbol,"buyOrders",9025125801)
"""
