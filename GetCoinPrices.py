import requests

class GetCoinPrices:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/ticker/price"

    def get_current_price(self, symbol):
        try:
            url = f"{self.base_url}?symbol={symbol}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return float(response.json()["price"])
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return -1