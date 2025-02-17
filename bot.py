import os
from BinanceTrader import BinanceTrader
import PriceUpdater
from dotenv import load_dotenv
import threading
from ReadExcellData import ReadExcelData
import time
import json
import TelegramMessageSender
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
        

        for sheet_name in sheet_names:
            symbol = sheet_name  # Ensure symbol is a string
            print("symbol", symbol)
            if BULK_PURCHASE_FLAG:
                bulkPurchase(symbol, readExcelData, trader,data)
                BULK_PURCHASE_FLAG = False


def getCurrentPrice(coin_name):
    with open(DB_OUTPUT_FILE_PATH, 'r') as file:
        data = json.load(file)
        print("data", data)
        return data.get(coin_name, "Coin not found")


"""
alış fiyatına bak
alış fiyatının üstündeki değerlerde elimizdeki total para kadar alım yapılacak bu alım market emir olacak
ama burada baslangic yoksay değeri varsa o değer kadar alım yapılmayacak üstündeki değerlerde alım yapılacak
yapılan alımlar kaydedilecek ve sonrasında biraz beklenip alt kısımlarda elimizdeki adeti sağlayacak kadar alış yapılacak
"""
def bulkPurchase(symbol, readExcelData, trader,data):
    currentPrice = getCurrentPrice(symbol)
    binanceMoney=100000
    bankMoney = 100000
    binanceMoney = trader.get_usdt_balance()/2
    bankMoney=binanceMoney
    if bankMoney is None:
        telegram_sender.send_message("Banka Hesabınızda Yeterli Bakiye Yok Error")
        print("Banka Hesabınızda Yeterli Bakiye Yok Error")
        return
    closest_indices = readExcelData.get_value_index("Fiyatlar", currentPrice)
    # closest_indices ten başlayarak üstündeki değerlerde alış yapılacak bankAmount kadar alış yapılacak
    print("closest_indices", closest_indices)
    totalBuyQuantity = 0
    for i in range(closest_indices[0], 0, -1):
        buy_price = readExcelData.get_cell_data(i, "Fiyatlar")
        buy_quantity = readExcelData.get_cell_data(i, "Alis Adet")
        sell_quantity = readExcelData.get_cell_data(i, "Satis Adet")
        start_ignore = readExcelData.get_cell_data(i, "BaslangicYoksay")

        
        # start ignore nan değilse alis yapılacak
        if start_ignore=="ok":
            print("bos geciliyor alim yapilmadi", start_ignore)
            continue
        if buy_price > currentPrice:
            bankMoney -= buy_price * buy_quantity
            if bankMoney < 0:
                telegram_sender.send_message("Banka Hesabınızda Yeterli Bakiye Yok")
                print("Banka Hesabınızda Yeterli Bakiye Yok")
                break
            totalBuyQuantity += buy_quantity
            print("currentPrice", currentPrice)
            print("buy_price", buy_price)
            print("totalBuyQuantity", totalBuyQuantity)
            # bu sadece veriye eklenmesi icin yapılır bir emir gondermez telegrama mesaj iletilir
            #trader.sell(symbol, buy_price, sell_quantity, MARKET, test=True)
    print("Toplu alım bitti totalBuyQuantity", totalBuyQuantity)
    telegram_sender.send_message("Toplu alım bitti totalBuyQuantity", totalBuyQuantity)
    ## şimdi adetler belirlendi anlık fiyat üzerinden market emir ile total adet üzerinden alım yapılacak
    trader.buy(symbol, currentPrice, totalBuyQuantity, MARKET)
    #simdi emirlerin gerçeklesmesini bekleyeceğiz buraya bir while atıp burada alim adeti ile hesabımızdaki adet esit oluncaya kadar bekleyeceğiz.
    while 1:
        coinBalance = trader.get_coin_balance(symbol)
        if coinBalance >= totalBuyQuantity:
            print("Alım işlemi tamamlandı")
            break
        time.sleep(10)
    # şimdi satış emirlerinin verilmesi gerekmekte
   
    totalBuyQuantity = 0
    for i in range(closest_indices[0], 0, -1):
        buy_price = readExcelData.get_cell_data(i, "Fiyatlar")
        buy_quantity = readExcelData.get_cell_data(i, "Alis Adet")
        sell_quantity = readExcelData.get_cell_data(i, "Satis Adet")
        start_ignore = readExcelData.get_cell_data(i, "BaslangicYoksay")

        
        # start ignore nan değilse alis yapılacak
        if start_ignore=="ok":
            print("bos geciliyor alim yapilmadi", start_ignore)
            continue
        if buy_price > currentPrice:
            binanceMoney -= buy_price * buy_quantity
            if binanceMoney < 0:
                print("Banka Hesabınızda Yeterli Bakiye Yok")
                break
            totalBuyQuantity += buy_quantity
            print("currentPrice", currentPrice)
            print("buy_price", buy_price)
            print("totalBuyQuantity", totalBuyQuantity)
            # bu sefer gercek satis emirleri verilecek
            trader.sell(symbol, buy_price, sell_quantity, LIMIT)
    # satis emirleri verildi simdi alis emirleri verilecek

    telegram_sender.send_message("Satis emirleri verildi simdi alis emirleri verilecek!")

    totalBuyQuantity = 0
    binanceMoney = trader.get_usdt_balance()/2
    bankMoney=binanceMoney
    for i in range(closest_indices[0], data.shape[0]):
        buy_price = readExcelData.get_cell_data(i, "Fiyatlar")
        buy_quantity = readExcelData.get_cell_data(i, "Alis Adet")
        sell_quantity = readExcelData.get_cell_data(i, "Satis Adet")
        start_ignore = readExcelData.get_cell_data(i, "BaslangicYoksay")

        
        # start ignore nan değilse alis yapılacak
        if start_ignore=="ok":
            print("bos geciliyor alim yapilmadi", start_ignore)
            continue
        if currentPrice > buy_price:
            bankMoney -= buy_price * buy_quantity
            if bankMoney < 0:
                telegram_sender.send_message("Banka Hesabınızda Yeterli Bakiye Yok")
                print("Banka Hesabınızda Yeterli Bakiye Yok")
                break
            totalBuyQuantity += buy_quantity
            print("currentPrice", currentPrice)
            print("buy_price", buy_price)
            print("totalBuyQuantity", totalBuyQuantity)

    telegram_sender.send_message("Toplu alım bitti ")
        
