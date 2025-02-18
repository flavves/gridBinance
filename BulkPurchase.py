import time
import json
class BulkPurchase:
    def __init__(self,trader, readExcelData,symbol,DB_OUTPUT_FILE_PATH,telegram_sender, data ):
        self.symbol = symbol
        self.readExcelData = readExcelData
        self.trader = trader
        self.data = data
        self.telegram_sender = telegram_sender
        self.DB_OUTPUT_FILE_PATH = DB_OUTPUT_FILE_PATH
        self.currentPrice = self.getCurrentPrice(symbol)
        self.binanceMoney = trader.get_usdt_balance() / 2
        self.bankMoney = -1


    def getCurrentPrice(self,coin_name):
        with open(self.DB_OUTPUT_FILE_PATH, 'r') as file:
            data = json.load(file)
            print("data", data)
            return data.get(coin_name, "Coin not found")


    def execute_bulk_purchase(self):
        if self.binanceMoney is None:
            self.telegram_sender.send_message("Banka Hesabınızda Yeterli Bakiye Yok Error")
            print("Banka Hesabınızda Yeterli Bakiye Yok Error")
            return

        closest_indices = self.readExcelData.get_value_index("Fiyatlar", self.currentPrice)
        print("closest_indices", closest_indices)
        totalBuyQuantity = 0

        for i in range(closest_indices[0], 0, -1):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                bankMoney=bankMoney/2

            if start_ignore == "ok":
                print("bos geciliyor alim yapilmadi", start_ignore)
                continue
            if buy_price > self.currentPrice:
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("Banka Hesabınızdaki para toplu alim icin bitmistir")
                    print("Banka Hesabınızdaki para toplu alim icin bitmistir")
                    break
                totalBuyQuantity += buy_quantity
                print("currentPrice", self.currentPrice)
                print("buy_price", buy_price)
                print("totalBuyQuantity", totalBuyQuantity)

        print("Toplu alım bitti totalBuyQuantity", totalBuyQuantity)
        self.telegram_sender.send_message(f"Toplu alım bitti totalBuyQuantity {totalBuyQuantity}")
        self.trader.buy(self.symbol, self.currentPrice, totalBuyQuantity, "MARKET")

        while True:
            coinBalance = self.trader.get_coin_balance(self.symbol)
            if coinBalance >= totalBuyQuantity:
                print("Alım işlemi tamamlandı")
                self.telegram_sender.send_message("Toplu alım emirleri gerçekleşti satış ve alım emirleri verilecek.")
                break
            time.sleep(10)

        #sell orders
        totalBuyQuantity = 0
        for i in range(closest_indices[0], 0, -1):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                bankMoney=bankMoney/2

            if start_ignore == "ok":
                print("bos geciliyor alim yapilmadi", start_ignore)
                continue
            if buy_price > self.currentPrice:
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("Banka Hesabındaki para toplu satış emirleri için bitmiştir")
                    print("Banka Hesabındaki para toplu satış emirleri için bitmiştir")
                    break
                totalBuyQuantity += buy_quantity
                print("currentPrice", self.currentPrice)
                print("buy_price", buy_price)
                print("totalBuyQuantity", totalBuyQuantity)
                self.trader.sell(self.symbol, buy_price, sell_quantity, "LIMIT")

        self.telegram_sender.send_message("Satis emirleri verildi simdi alis emirleri verilecek!")

        totalBuyQuantity = 0
        self.binanceMoney = self.trader.get_usdt_balance() / 2
        self.bankMoney = self.binanceMoney
        for i in range(closest_indices[0], self.data.shape[0]):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                bankMoney=bankMoney/2

            if start_ignore == "ok":
                print("bos geciliyor alim yapilmadi", start_ignore)
                continue
            if self.currentPrice > buy_price:
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("Banka Hesabındaki para toplu alım emirleri için bitmiştir")
                    print("Banka Hesabındaki para toplu alım emirleri için bitmiştir")
                    break
                totalBuyQuantity += buy_quantity
                print("currentPrice", self.currentPrice)
                print("buy_price", buy_price)
                print("totalBuyQuantity", totalBuyQuantity)

        self.telegram_sender.send_message("Toplu alım bitti Grid bot başlamıştır başarılar :)")
