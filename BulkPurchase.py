import time
import json
import requests
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


    def getCurrentPrice(self,symbol):
        try:
            base_url = "https://api.binance.com/api/v3/ticker/price"
            url = f"{base_url}?symbol={symbol}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return float(response.json()["price"])
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return -1


    def execute_bulk_purchase(self):
        print("Toplu alım başladı")
        print("Binance hesabında bulunan para", self.binanceMoney)
        
        if self.binanceMoney is None:
            self.telegram_sender.send_message("Banka Hesabınızda Yeterli Bakiye Yok Error")
            print("Banka Hesabınızda Yeterli Bakiye Yok Error")
            return
        if self.currentPrice is None or self.currentPrice == -1:
            self.telegram_sender.send_message("Anlık fiyat alınamadı")
            print("Anlık fiyat alınamadı Durduruluyor")
            return
        print("toplu alım için anlık fiyata en yakın fiyatlar alınıyor")
        closest_indices = self.readExcelData.get_value_index("Fiyatlar", self.currentPrice)
        totalBuyQuantity = 0
        print("toplu alım için en yakın fiyatlar alındı kaç adet alınacağı hesaplanıyor")
        for i in range(closest_indices[0], 0, -1):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                self.bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                print("Bütçe olarak kullanılacak para", self.bankMoney)
                self.bankMoney=self.bankMoney/2
            if self.bankMoney < 0:
                self.telegram_sender.send_message("butce excell üzerinden alınmadı")
                print("butce excell üzerinden alınmadı")
                break
            

            if start_ignore == "ok":
                print("bos geciliyor alim yapilmadi", buy_price)
                continue
            print ("buy_price", buy_price)
            print ("self.currentPrice", self.currentPrice)
            if buy_price > self.currentPrice:
                print("toplu alım için uygun fiyat bulundu")
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("Banka Hesabınızdaki para toplu alim icin bitmistir")
                    print("Banka Hesabınızdaki para toplu alim icin bitmistir")
                    break
                totalBuyQuantity += buy_quantity
                print("--------------------------")
                print("currentPrice", self.currentPrice)
                print("buy_price", buy_price)
                print("totalBuyQuantity", totalBuyQuantity)
                print("bankMoney", self.bankMoney)
                print("--------------------------")
        if totalBuyQuantity == 0:
            self.telegram_sender.send_message("Toplu alım için uygun fiyat bulunamadı")
            print("Toplu alım için uygun fiyat bulunamadı")
            return
        
        print("Toplu alım bitti totalBuyQuantity", totalBuyQuantity)

        self.telegram_sender.send_message(f"Toplu alım bitti totalBuyQuantity {totalBuyQuantity}")
        order=self.trader.buy(self.symbol,"MARKET",totalBuyQuantity, self.currentPrice)

        print("Market emri --> ",totalBuyQuantity, "adet için alım emri verildi")
        print("Emir detayları --> ",order)
        while True:
            coinName = self.symbol.split("USDT")[0]
            coinBalance = self.trader.get_coin_balance(coinName)
            print("hesapta alınan coin miktarı kontrol ediliyor --> ",coinBalance,"/",totalBuyQuantity)
            try:
                if coinBalance >= totalBuyQuantity:
                    print("Alım işlemi tamamlandı")
                    self.telegram_sender.send_message("Toplu alım emirleri gerçekleşti satış ve alım emirleri verilecek.")
                    break
            except:
                print("Alım daha tamamlanmadı")
            time.sleep(10)

        #sell orders
        print("satış emri veriliyor")
        self.bankMoney=-1
        totalBuyQuantity = 0
        for i in range(closest_indices[0], 0, -1):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                self.bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                self.bankMoney=self.bankMoney/2

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
                print("--------------------------")
                print("currentPrice", self.currentPrice)
                print("buy_price", buy_price)
                print("totalBuyQuantity", totalBuyQuantity)
                print("--------------------------")
                self.trader.sell(self.symbol,"LIMIT",sell_quantity, buy_price)
        
        self.telegram_sender.send_message("Satis emirleri verildi simdi alis emirleri verilecek!")
        print("alış emri veriliyor.")
        totalBuyQuantity = 0
        self.bankMoney=-1
        for i in range(closest_indices[0], self.data.shape[0]):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                self.bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                self.bankMoney=self.bankMoney/2

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
                self.trader.buy(self.symbol,"LIMIT",buy_quantity, buy_price)
        self.telegram_sender.send_message("Toplu alım bitti Grid bot başlamıştır başarılar :)")
