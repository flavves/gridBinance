import os
from BinanceTrader import BinanceTrader
import PriceUpdater
from dotenv import load_dotenv
import threading
from ReadExcellData import ReadExcelData
import time
LIMIT="LIMIT"
MARKET="MARKET"
load_dotenv()
 
def startBinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID):  
    trader = BinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    return trader

def startPriceUpdater(trades_file, output_file, interval=10):
    price_updater = PriceUpdater.PriceUpdater(trades_file, output_file, interval)
    price_updater.start()
    return price_updater

def run_bot():

    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_API_SECRET')
    home_dir = os.path.expanduser('~')
    DB_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'trades.json')
    DB_OUTPUT_FILE_PATH=os.path.join(home_dir, 'python', 'gridBinance', 'current_prices.json')
    EXCELL_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'files', 'grid.xlsx')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    print("PriceUpdater Başlatılıyor thread")
    t1 = threading.Thread(target=startPriceUpdater, args=(DB_FILE_PATH, DB_OUTPUT_FILE_PATH, 10))
    t1.start()

    print("PriceUpdater Başlatıldı")

    print("BinanceTrader Başlatılıyor")
    
    trader = startBinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    print("BinanceTrader Başlatıldı")
    readExcelData = ReadExcelData(EXCELL_FILE_PATH)
    while 1:
        time.sleep(1)
        readExcelData.read_data()
        data = readExcelData.get_data()
        if data is not None:
            print(data.head())