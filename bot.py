import os
from BinanceTrader import BinanceTrader
import PriceUpdater
from dotenv import load_dotenv
import threading
from ReadExcellData import ReadExcelData
import time
import json
import TelegramMessageSender
from BulkPurchase import BulkPurchase
LIMIT="LIMIT"
MARKET="MARKET"
load_dotenv()
 
#defines
global API_KEY, API_SECRET, DB_FILE_PATH,DB_OUTPUT_FILE_PATH,EXCELL_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
#flags
global BULK_PURCHASE_FLAG
BULK_PURCHASE_FLAG = True
#objects
global telegram_sender




def startBinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID):  
    trader = BinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    return trader

def startPriceUpdater(trades_file, output_file, interval=10):
    price_updater = PriceUpdater.PriceUpdater(trades_file, output_file, interval)
    price_updater.start()
    return price_updater

def run_bot():
    global API_KEY, API_SECRET, DB_FILE_PATH,DB_OUTPUT_FILE_PATH,EXCELL_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    global BULK_PURCHASE_FLAG
    global telegram_sender
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_API_SECRET')
    home_dir = os.path.expanduser('~')
    DB_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'trades.json')
    DB_OUTPUT_FILE_PATH=os.path.join(home_dir, 'python', 'gridBinance', 'current_prices.json')
    EXCELL_FILE_PATH = os.path.join(home_dir, 'python', 'gridBinance', 'files', 'grid.xlsx')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    telegram_sender = TelegramMessageSender.TelegramMessageSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)


    print("PriceUpdater Başlatılıyor thread")
    t1 = threading.Thread(target=startPriceUpdater, args=(DB_FILE_PATH, DB_OUTPUT_FILE_PATH, 10))
    t1.start()

    print("PriceUpdater Başlatıldı")

    print("BinanceTrader Başlatılıyor")
    
    trader = startBinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    print("BinanceTrader Başlatıldı")
    
    while 1:
        readExcelData = ReadExcelData(EXCELL_FILE_PATH)
        time.sleep(1)
        readExcelData.read_data()
        data = readExcelData.get_data()
        if data is not None:
            print(data.head())
        sheet_names = readExcelData.get_sheet_names()
        
        print("excel verileri kontrol ediliyor.")
        for sheet_name in sheet_names:
            symbol = sheet_name  # Ensure symbol is a string
            print("symbol -->", symbol)
            if BULK_PURCHASE_FLAG:
                
                bulkPurchase = BulkPurchase(trader, readExcelData, symbol, DB_OUTPUT_FILE_PATH, telegram_sender,data)
                bulkPurchase.execute_bulk_purchase()
                BULK_PURCHASE_FLAG = False


def getCurrentPrice(coin_name):
    with open(DB_OUTPUT_FILE_PATH, 'r') as file:
        data = json.load(file)
        print("data", data)
        return data.get(coin_name, "Coin not found")

