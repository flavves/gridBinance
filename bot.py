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
from logging.handlers import TimedRotatingFileHandler
import DBManager
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    DB_FILE_PATH = os.path.join(base_dir, 'trades.json')
    DB_OUTPUT_FILE_PATH = os.path.join(base_dir, 'current_prices.json')
    EXCELL_FILE_PATH = os.path.join(base_dir, 'files', 'grid.xlsx')
    STATE_FILE = os.path.join(base_dir, 'botStates.json')
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
        
        #logging.info("Checking Excel data.")
        for sheet_name in sheet_names:
            symbol = sheet_name  # Ensure symbol is a string
            #logging.info(f"Symbol: {symbol}")
            symbolPrice = trader.get_current_price(symbol)
            if symbolPrice is None or symbolPrice == -1:
                telegram_sender.send_message(f"🧨 Fiyat alınırken hata oluştu {symbol}.")
                logging.error(f"An error occurred while retrieving the price for {symbol}.")
                continue

            # Check the state of the coin
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
                f.close()
            
            if symbol in state:
                if state[symbol] == "started":
                    bulkPurchase = BulkPurchase(trader, readExcelData, symbol, DB_OUTPUT_FILE_PATH, telegram_sender, data)
                    result=bulkPurchase.execute_bulk_purchase()
                    if result != -1:
                        state[symbol] = "completed"
                        with open(STATE_FILE, "w") as f:
                            json.dump(state, f)
                            f.close()
                        logging.info(f"Bulk purchase executed for {symbol}.")
                    else:
                        logging.error("bulk is failed wait 10 sec")
                        time.sleep(10)
                    
                elif state[symbol] == "completed":
                    #logging.info(f"Bulk purchase not allowed for {symbol} as it is already completed.")

                    # bota burada devam ediyoruz simdi 
                    # herhangi bir emir gerçekleşti mi diye bakmamız gerekiyor ilgili coin için
                    # Trades.json içine ilgili koinin emirlerine bakıyoruz. Bir emir gerçekleştiyse listeden siliyoruz
                    # gerçekleşen emir alış ise listedeki bir alttaki değere alış giriyoruz ve grid aralık degerine bakıyoruz
                    # grid aralık degerimizde bir satış yoksa oraya satış veriyoruz. 0.23 alışı oldu şimdi 0.26 ya satış giriyorum.
                    # 1 grid aralık degerini  alıyorum 
                    gridAralik=readExcelData.get_cell_data(0, "GRID ARALIK")
                    # trades.json içine bakıyorum anlık fiyat için bir emir gerçekleşmiş mi bakıyorum.
                    
                    #db yi yükle
                    db_manager = DBManager.DBManager(DB_FILE_PATH)
                    
                    try:
                        trades=db_manager.get_all_trades()
                    except:
                        logging.error("cannot find trades file.")
                        return
                    if trades is not None:
                        logging.info(f"Trades: {trades}")
                    if symbol in trades:
                        
                        buy_orders = trades[symbol].get("buyOrders", [])
                        sell_orders = trades[symbol].get("sellOrders", [])
                        #logging.info(f"Buy Orders for {symbol}: {buy_orders}")
                        #logging.info(f"Sell Orders for {symbol}: {sell_orders}")
                        # order id değerlerine bakılcak ve gerçekleşen emirler silinecek
                        orderFilledFlag=False
                        for order in buy_orders:
                            order_id = order["orderId"]
                            status = trader.check_order_status(symbol, order_id)
                            orderFilledFlag=False
                            if status == "FILLED":
                                orderFilledFlag=True
                                logging.info(f"Order {order_id} is filled.")
                                db_manager.delete_trade(symbol,"buyOrders",order_id)
                                # gerçekleşen alış emri olduğu için satış emri verilecek
                                # alış fiyatından grid aralık kadar yukarıda satış emri verilecek
                                # alış fiyatı
                                buy_price=order["price"]
                                # satış fiyatı
                                sell_price=float(buy_price)+float(gridAralik)
                                logging.info(f"buy_price: {buy_price}, sell_price: {sell_price}, gridAralik: {gridAralik}")
                                # satış emri verilecek fiyat icin en yakin index aliniyor
                                closest_indices = readExcelData.get_value_index("Fiyatlar", sell_price)
                                if closest_indices is None:
                                    logging.error(f"Could not find a closest index for buy price {buy_price}.")
                                    continue
                                sell_price = readExcelData.get_cell_data(closest_indices[0], "Fiyatlar")
                                try:
                                    logging.info(f"NEW sell_price: {sell_price}, sell_price Index: {closest_indices[0]}")
                                except:
                                    pass
                                #eğer buy_price için daha önceden bir emir verilmediyse
                                if str(sell_price) not in [order["price"] for order in sell_orders]:
                                    quantity=readExcelData.get_cell_data(closest_indices[0], "Satis Adet")
                                    logging.info(f"EMIR VERILIYOR SATIS quantity: {quantity}, symbol: {symbol}, sell_price: {sell_price}")
                                    while True:
                                        coinName = symbol.split("USDT")[0]
                                        coinBalance = trader.get_coin_balance(coinName)
                                        logging.info(f"Hesapta alınan coin miktarı kontrol ediliyor coinBalance / quantity: {coinBalance} / {quantity}")
                                        telegram_sender.send_message(f"Hesapta alınan coin miktarı kontrol ediliyor coinBalance / quantity: {coinBalance} / {quantity}")
                                        try:
                                            if coinBalance >= quantity:
                                                logging.info("Satış Emir icin gerekli adet Karşılandı")
                                                telegram_sender.send_message("🛎 Satış Emir icin gerekli adet Karşılandı")
                                                break
                                        except:
                                            logging.info("Alım daha tamamlanmadı")
                                        time.sleep(10)
                                    sell_order=trader.sell(symbol,"LIMIT",quantity, sell_price)
                                    if sell_order is not None:
                                        logging.info(f"Order {sell_order} is created for {symbol}.")
                                    else:
                                        logging.error(f"An error occurred while creating a sell order for {symbol}.")
            
                                    #elde fazladan koin varsa onun da satisini ver
                                    try:
                                        time.sleep(2)
                                        # elde eğer satış yapacak kadar o sembolden para birikirse satış yapılacak listeye dayanarak.
                                        try:
                                            trades=db_manager.get_all_trades()
                                        except:
                                            logging.error("cannot find trades file.")
                                            return
                                        if trades is not None:
                                            pass
                                            #logging.info(f"Trades: {trades}")
                                        if symbol in trades:
                                            
                                            sell_orders = trades[symbol].get("sellOrders", [])
                                            for order in sell_orders:
                                                coinName = symbol.split("USDT")[0]
                                                holdingSymbol=trader.get_coin_balance(coinName)
                                                if holdingSymbol is None:
                                                    logging.error("binance api error. Cannot get coin balance")
                                                    continue
                                                time.sleep(1)    
                                                max_sell_price = max(float(order["price"]) for order in sell_orders)
                                                new_sell_price = float(max_sell_price) + float(gridAralik)
                                                logging.info(f"Artik alis Mevcut en yüksek satış fiyatı: {max_sell_price}")
                                                logging.info(f"Artik alis Yeni satış fiyatı: {new_sell_price}")   
                                                closest_indices = readExcelData.get_value_index("Fiyatlar", new_sell_price)
                                                if closest_indices is None:
                                                    logging.error(f"Artik alis Could not find a closest index for buy price {new_sell_price}.")
                                                    continue
                                                sell_price = readExcelData.get_cell_data(closest_indices[0], "Fiyatlar")
                                                #eğer buy_price için daha önceden bir emir verilmediyse
                                                if str(sell_price) not in [order["price"] for order in sell_orders]:
                                                    quantity=readExcelData.get_cell_data(closest_indices[0], "Satis Adet")
                                                    if float(holdingSymbol) >= float(quantity):
                                                        #simdi satıs emri verilebilir.
                                                        sell_order=trader.sell(symbol,"LIMIT",quantity, sell_price)
                                                        if sell_order is not None:
                                                            logging.info(f"Artik alis Order {sell_order} is created for {symbol}.")
                                                        else:
                                                            logging.error(f"Artik alis An error occurred while creating a sell order for {symbol}.")
                                        
                                    except:
                                        logging.error("artik alis hatasi")                
                                    ##
                                    
                                    
                                    
                                else:
                                    logging.info(f"Order for {buy_price} already exists. Nothing to do.")
                        if orderFilledFlag==True:
                            continue
                        orderFilledFlag=False
                        for order in sell_orders:
                            order_id = order["orderId"]
                            status=trader.check_order_status(symbol, order_id)
                            orderFilledFlag=False
                            if status=="FILLED":
                                orderFilledFlag=True
                                logging.info(f"Order {order_id} is filled.")
                                time.sleep(0.1)
                                db_manager.delete_trade(symbol,"sellOrders",order_id)
                                # gerçekleşen satış emri olduğu için alış emri verilecek
                                # satış fiyatı
                                sell_price=order["price"]
                                # alış fiyatı
                                buy_price=float(sell_price)-float(gridAralik)
                                logging.info(f"buy_price: {buy_price}, sell_price: {sell_price}, gridAralik: {gridAralik}")

                                # alış emri verilecek fiyat icin en yakin index aliniyor
                                closest_indices = readExcelData.get_value_index("Fiyatlar", buy_price)
                                if closest_indices is None:
                                    logging.error(f"Could not find a closest index for buy price {buy_price}.")
                                    continue
                                buy_price = readExcelData.get_cell_data(closest_indices[0], "Fiyatlar")
                                try:
                                    logging.info(f"NEW buy_price: {buy_price}, buy_price Index: {closest_indices[0]}")
                                except:
                                    pass
                                #eğer buy_price için daha önceden bir emir verilmediyse
                                
                                if str(buy_price) not in [order["price"] for order in buy_orders]:
                                    
                                    quantity=readExcelData.get_cell_data(closest_indices[0], "Alis Adet")
                                    logging.info(f"EMIR VERILIYOR ALIS quantity: {quantity}, symbol: {symbol}, buy_price: {buy_price}")

                                    buy_order=trader.buy(symbol,"LIMIT",quantity, buy_price)
                                    if buy_order is not None:
                                        logging.info(f"Order {buy_order} is created for {symbol}.")
                                    else:
                                        logging.error(f"An error occurred while creating a buy order for {symbol}.")
                                else:
                                    logging.info(f"Order for {buy_price} already exists. Nothing to do.")
                        if orderFilledFlag==True:
                            continue
                                    
                                                
            else:
                logging.info(f"{symbol} is not in the state file.")
