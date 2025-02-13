import json
import threading
import time
import requests
from GetCoinPrices import GetCoinPrices

class PriceUpdater:
    def __init__(self, trades_file, output_file, interval=10):
        self.trades_file = trades_file
        self.output_file = output_file
        self.interval = interval
        self.coin_prices = GetCoinPrices()
        self.running = False
        self.lock = threading.Lock()

    def load_trades(self):
        with open(self.trades_file, 'r') as file:
            self.trades = json.load(file)

    def update_price(self, symbol):
        while self.running:
            price = self.coin_prices.get_current_price(symbol)
            if price != -1:
                with self.lock:
                    with open(self.output_file, 'r') as file:
                        prices = json.load(file)
                    prices[symbol] = price
                    with open(self.output_file, 'w') as file:
                        json.dump(prices, file, indent=4)
            time.sleep(self.interval)

    def start(self):
        self.load_trades()
        self.running = True
        self.threads = []
        for symbol in self.trades.keys():
            thread = threading.Thread(target=self.update_price, args=(symbol,))
            thread.daemon = True  # Set the thread as a daemon
            thread.start()
            self.threads.append(thread)

    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join()
"""
# Usage example
if __name__ == "__main__":
    trades_file = "/home/batuhanokmen/python/gridBinance/trades.json"
    output_file = "/home/batuhanokmen/python/gridBinance/current_prices.json"
    price_updater = PriceUpdater(trades_file, output_file, interval=10)
    price_updater.start()
    # The main thread can continue doing other tasks
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            price_updater.stop()
            break
"""