from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
import pandas as pd
import os
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

class TelegramBotRunner:
    def __init__(self, token):
        self.token = token
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.app.add_handler(CommandHandler("chatid", self.handle_chatid))
        self.app.add_handler(CommandHandler("start", self.handle_start))
        self.app.add_handler(CommandHandler("stop", self.handle_stop))
        self.app.add_handler(CommandHandler("binanceToken", self.handle_apikey))
        self.app.add_handler(CommandHandler("binanceSecret", self.handle_apisecret))
        base_dir = os.path.dirname(os.path.abspath(__file__))
        STATE_FILE = os.path.join(base_dir, 'botStates.json')
        self.state_file = STATE_FILE
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.state = json.load(f)
        else:
            self.state = {}

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f)

    async def handle_start(self, update: Update, context) -> None:
        pair = context.args[0] if context.args else None
        if pair:
            self.state[pair] = "started"
            self.save_state()
            await update.message.reply_text(f"{pair} için bot başlatıldı. 🎉")
        else:
            await update.message.reply_text("📍 Lütfen bir çift belirtin. Örnek: /start BTCUSDT")

    async def handle_stop(self, update: Update, context) -> None:
        pair = context.args[0] if context.args else None
        if pair and pair in self.state:
            del self.state[pair]
            self.save_state()
            await update.message.reply_text(f"{pair} için bot durduruldu ve kayıt silindi.🧼")
        else:
            await update.message.reply_text("📍 Lütfen geçerli bir çift belirtin. Örnek: /stop BTCUSDT")

    async def handle_document(self, update: Update, context) -> None:
        file = update.message.document
        if file.mime_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
            file_id = file.file_id
            new_file = await context.bot.get_file(file_id)
            file_path = f"./{file.file_name}"
            await new_file.download_to_drive(file_path)

            # Excel dosyasını oku
            df = pd.read_excel(file_path)

            # İlk 5 satırı gönder
            await update.message.reply_text(f"🗒 İlk 5 satır:\n{df.head().to_string()}")

            # Dosyayı sil
            os.remove(file_path)
        else:
            await update.message.reply_text("📍 Lütfen sadece Excel dosyası gönderin!")

    async def handle_chatid(self, update: Update, context) -> None:
        chat_id = update.message.chat_id
        await update.message.reply_text(f"📪 Chat ID: {chat_id}")

    #api keyi apikey.json dosyasına kaydet
    async def handle_apikey(self, update: Update, context) -> None:
        if context.args:
            api_key = context.args[0]
            with open("apikey.json", "w") as f:
                json.dump({"api_key": api_key}, f)
            await update.message.reply_text("📦 API Key kaydedildi.")
        else:
            await update.message.reply_text("📍 Lütfen bir API Key belirtin. Örnek: /binanceToken YOUR_API_KEY")

    #api secreti apisecret.json dosyasına kaydet
    async def handle_apisecret(self, update: Update, context) -> None:
        if context.args:
            api_secret = context.args[0]
            with open("apisecret.json", "w") as f:
                json.dump({"api_secret": api_secret}, f)
            await update.message.reply_text("📦 API Secret kaydedildi.")
        else:
            await update.message.reply_text("📍 Lütfen bir API Secret belirtin. Örnek: /binanceSecret YOUR_API_SECRET")

    def start(self):
        self.app.run_polling()
    
    

if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    bot_runner = TelegramBotRunner(TELEGRAM_BOT_TOKEN)
    bot_runner.start()
