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
    STATE_FILE = os.path.join(home_dir, 'python', 'gridBinance', 'botStates.json')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    telegram_sender = TelegramMessageSender.TelegramMessageSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    trader = startBinanceTrader(API_KEY, API_SECRET, DB_FILE_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    while 1:
        readExcelData = ReadExcelData(EXCELL_FILE_PATH)
        time.sleep(3)
        readExcelData.read_data()
        data = readExcelData.get_data()

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

            # Check the state of the coin
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
            
            if symbol in state:
                if state[symbol] == "started":
                    bulkPurchase = BulkPurchase(trader, readExcelData, symbol, DB_OUTPUT_FILE_PATH, telegram_sender, data)
                    bulkPurchase.execute_bulk_purchase()
                    state[symbol] = "completed"
                    with open(STATE_FILE, "w") as f:
                        json.dump(state, f)
                    logging.info(f"Bulk purchase executed for {symbol}.")
                elif state[symbol] == "completed":
                    logging.info(f"Bulk purchase not allowed for {symbol} as it is already completed.")

                    # bota burada devam ediyoruz simdi 
                    # herhangi bir emir gerçekleşti mi diye bakmamız gerekiyor ilgili coin için
                    # Trades.json içine ilgili koinin emirlerine bakıyoruz. Bir emir gerçekleştiyse listeden siliyoruz
                    # gerçekleşen emir alış ise listedeki bir alttaki değere alış giriyoruz ve grid aralık degerine bakıyoruz
                    # grid aralık degerimizde bir satış yoksa oraya satış veriyoruz. 0.23 alışı oldu şimdi 0.26 ya satış giriyorum.
                    # 1 grid aralık degerini  alıyorum 
                    gridAralik=readExcelData.get_cell_data(0, "GRID ARALIK")
                    # trades.json içine bakıyorum anlık fiyat için bir emir gerçekleşmiş mi bakıyorum.
                    with open(DB_FILE_PATH, "r") as f:
                        trades = json.load(f)
                    if trades is not None:
                        logging.info(f"Trades: {trades}")
                    if symbol in trades:
                        buy_orders = trades[symbol].get("buyOrders", [])
                        sell_orders = trades[symbol].get("sellOrders", [])
                        logging.info(f"Buy Orders for {symbol}: {buy_orders}")
                        logging.info(f"Sell Orders for {symbol}: {sell_orders}")
                        # symbolPrice eğer buy_orders içindeki bir değerden küçükse emir gerçekleşmiştir. o emri siliyoruz
                        for i in range(len(buy_orders)):
                            if symbolPrice < buy_orders[i]["price"]:
                                del buy_orders[i]
                                break
                        


            else:
                logging.info(f"{symbol} is not in the state file.")
