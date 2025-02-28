import time
import json
import requests
import logging  # Added logging import

class BulkPurchase:
    def __init__(self,trader, readExcelData,symbol,DB_OUTPUT_FILE_PATH,telegram_sender, data ):
        self.symbol = symbol
        self.readExcelData = readExcelData
        self.trader = trader
        self.data = data
        self.telegram_sender = telegram_sender
        self.DB_OUTPUT_FILE_PATH = DB_OUTPUT_FILE_PATH
        self.currentPrice = self.getCurrentPrice(symbol)
        self.binanceMoney = trader.get_usdt_balance()
        self.bankMoney = -1


    def getCurrentPrice(self,symbol):
        time.sleep(1)
        try:
            base_url = "https://api.binance.com/api/v3/ticker/price"
            url = f"{base_url}?symbol={symbol}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return float(response.json()["price"])
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {e}")
            return -1


    def execute_bulk_purchase(self):
        logging.info("Toplu alım başladı")
        logging.info(f"Binance hesabında bulunan para: {self.binanceMoney}")
        
        if self.binanceMoney is None or self.binanceMoney == -1:
            self.telegram_sender.send_message("🧨 Banka Hesabınızda Yeterli Bakiye Yok Error")
            logging.error("Banka Hesabınızda Yeterli Bakiye Yok Error")
            return -1
        if self.currentPrice is None or self.currentPrice == -1:
            self.telegram_sender.send_message("🧨 Anlık fiyat alınamadı")
            logging.error("Anlık fiyat alınamadı Durduruluyor")
            return -1
        logging.info("Toplu alım için anlık fiyata en yakın fiyatlar alınıyor")
        closest_indices = self.readExcelData.get_value_index("Fiyatlar", self.currentPrice)
        totalBuyQuantity = 0
        logging.info("Toplu alım için en yakın fiyatlar alındı, kaç adet alınacağı hesaplanıyor")
        for i in range(closest_indices[0], 0, -1):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                self.bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                satisOran= self.readExcelData.get_cell_data(0, "AlisOran")
                if self.binanceMoney < self.bankMoney:
                    self.telegram_sender.send_message("🧨 Banka Hesabınızdaki para Binance hesabınızdaki paradan fazla"
                                                      "Binance hesabınızdaki parayı arttırın")
                    logging.error("Banka Hesabınızdaki para Binance hesabınızdaki paradan fazla")
                    return -1
                satisOran= 1-satisOran
                self.bankMoney=self.bankMoney * satisOran
                
                logging.info(f"Satis oranı: {satisOran}, Bütçe: {self.bankMoney}")
            if self.bankMoney < 0:
                self.telegram_sender.send_message("🧨 butce excell üzerinden alınmadı")
                logging.error("Bütçe Excel üzerinden alınmadı")
                break
            

            if start_ignore == "ok":
                logging.info(f"Boş geçiliyor, alım yapılmadı: {buy_price}")
                continue
            logging.info(f"Buy price: {buy_price}, Current price: {self.currentPrice}")
            if buy_price > self.currentPrice:
                logging.info("Toplu alım için uygun fiyat bulundu")
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("🛎 Banka Hesabınızdaki para toplu alim icin bitmistir")
                    logging.error("Banka Hesabınızdaki para toplu alım için bitmiştir")
                    break
                totalBuyQuantity += buy_quantity
                logging.info(f"Current price: {self.currentPrice}, Buy price: {buy_price}, Total buy quantity: {totalBuyQuantity}, Bank money: {self.bankMoney}")
        if totalBuyQuantity == 0:
            self.telegram_sender.send_message("🧨 Toplu alım için uygun fiyat bulunamadı")
            logging.info("Toplu alım için uygun fiyat bulunamadı")
            return -1
        
        logging.info(f"Toplu alım bitti, total buy quantity: {totalBuyQuantity}")

        self.telegram_sender.send_message(f"🛎 Toplu alım bitti totalBuyQuantity {totalBuyQuantity}")
        order=self.trader.buy(self.symbol,"MARKET",totalBuyQuantity, self.currentPrice,isBulk=True)

        logging.info(f"Market emri: {totalBuyQuantity} adet için alım emri verildi")
        logging.info(f"Emir detayları: {order}")
        while True:
            coinName = self.symbol.split("USDT")[0]
            coinBalance = self.trader.get_coin_balance(coinName)
            logging.info(f"Hesapta alınan coin miktarı kontrol ediliyor: {coinBalance}/{totalBuyQuantity}")
            try:
                if coinBalance >= totalBuyQuantity:
                    logging.info("Alım işlemi tamamlandı")
                    self.telegram_sender.send_message("🛎 Toplu alım emirleri gerçekleşti satış ve alım emirleri verilecek. 🎊 ")
                    break
            except:
                logging.info("Alım daha tamamlanmadı")
            time.sleep(10)

        #sell orders
        logging.info("Satış emri veriliyor")
        self.bankMoney=-1
        totalBuyQuantity = 0
        for i in range(closest_indices[0], 0, -1):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                self.bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                satisOran= self.readExcelData.get_cell_data(0, "AlisOran")
                satisOran= 1-satisOran
                self.bankMoney=self.bankMoney * satisOran

            if start_ignore == "ok":
                logging.info(f"Boş geçiliyor, alım yapılmadı: {start_ignore}")
                continue
            if buy_price > self.currentPrice:
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("🛎 Banka Hesabındaki para toplu satış emirleri için bitmiştir")
                    logging.error("Banka Hesabındaki para toplu satış emirleri için bitmiştir")
                    break
                totalBuyQuantity += buy_quantity
                logging.info(f"Current price: {self.currentPrice}, Buy price: {buy_price}, Total buy quantity: {totalBuyQuantity}")
                self.trader.sell(self.symbol,"LIMIT",sell_quantity, buy_price)
        
        self.telegram_sender.send_message("Satis emirleri verildi simdi alis emirleri verilecek!")
        logging.info("Alış emri veriliyor.")
        totalBuyQuantity = 0
        self.bankMoney=-1
        for i in range(closest_indices[0], self.data.shape[0]):
            buy_price = self.readExcelData.get_cell_data(i, "Fiyatlar")
            buy_quantity = self.readExcelData.get_cell_data(i, "Alis Adet")
            sell_quantity = self.readExcelData.get_cell_data(i, "Satis Adet")
            start_ignore = self.readExcelData.get_cell_data(i, "BaslangicYoksay")
            if(self.bankMoney==-1):
                self.bankMoney= self.readExcelData.get_cell_data(0, "BUTCE")
                alisOran= self.readExcelData.get_cell_data(0, "AlisOran")

                self.bankMoney=self.bankMoney * alisOran
                logging.info(f"Alış oranı: {alisOran}, Bütçe: {self.bankMoney}")

            if start_ignore == "ok":
                logging.info(f"Boş geçiliyor, alım yapılmadı: {start_ignore}")
                continue
            if self.currentPrice > buy_price:
                self.bankMoney -= buy_price * buy_quantity
                if self.bankMoney < 0:
                    self.telegram_sender.send_message("🛎 Banka Hesabındaki para toplu alım emirleri için bitmiştir")
                    logging.error("Banka Hesabındaki para toplu alım emirleri için bitmiştir")
                    break
                totalBuyQuantity += buy_quantity
                logging.info(f"Current price: {self.currentPrice}, Buy price: {buy_price}, Total buy quantity: {totalBuyQuantity}")
                self.trader.buy(self.symbol,"LIMIT",buy_quantity, buy_price)
        self.telegram_sender.send_message("🛎 Toplu alım bitti Grid bot başlamıştır başarılar 💸💸💸🎊🎊🎊")
        return 1