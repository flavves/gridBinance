from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
import pandas as pd
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
class TelegramBotRunner:
    def __init__(self, token):
        self.token = token
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.app.add_handler(CommandHandler("chatid", self.handle_chatid))

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
            await update.message.reply_text(f"İlk 5 satır:\n{df.head().to_string()}")

            # Dosyayı sil
            os.remove(file_path)
        else:
            await update.message.reply_text("Lütfen sadece Excel dosyası gönderin!")

    async def handle_chatid(self, update: Update, context) -> None:
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Chat ID: {chat_id}")

    def start(self):
        self.app.run_polling()

if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    bot_runner = TelegramBotRunner(TELEGRAM_BOT_TOKEN)
    bot_runner.start()
