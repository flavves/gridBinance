import os
from BinanceTrader import BinanceTrader
from dotenv import load_dotenv
import threading
from ReadExcellData import ReadExcelData
import time
import json
import TelegramMessageSender
from BulkPurchase import BulkPurchase
import requests
import logging  # Added logging import

LIMIT="LIMIT"
MARKET="MARKET"
load_dotenv()

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    
    trader = startBinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    while 1:
        readExcelData = ReadExcelData(EXCELL_FILE_PATH)
        time.sleep(3)
        readExcelData.read_data()
        data = readExcelData.get_data()
        if data is not None:
            logging.info(f"Excel data: {data.head()}")
        sheet_names = readExcelData.get_sheet_names()
        
        logging.info("Checking Excel data.")
        for sheet_name in sheet_names:
            symbol = sheet_name  # Ensure symbol is a string
            logging.info(f"Symbol: {symbol}")
            symbolPrice = trader.get_current_price(symbol)
            if symbolPrice is None or symbolPrice == -1:
                telegram_sender.send_message(f"An error occurred while retrieving the price for {symbol}.")
                logging.error(f"An error occurred while retrieving the price for {symbol}.")
                continue         
            if BULK_PURCHASE_FLAG:
                bulkPurchase = BulkPurchase(trader, readExcelData, symbol, DB_OUTPUT_FILE_PATH, telegram_sender, data)
                bulkPurchase.execute_bulk_purchase()
                BULK_PURCHASE_FLAG = False
