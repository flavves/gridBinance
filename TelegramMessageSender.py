import requests
import logging
class TelegramMessageSender:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text):
        try:
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            data = {'chat_id': self.chat_id, 'text': text}
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logging.info("Message sent successfully")
                return "Message sent successfully"
            else:
                logging.error(f"Failed to send message: {response.status_code} - {response.text}")
                return f"Failed to send message: {response.status_code} - {response.text}"
        except:
            try:
                logging.error("Telegram mesaj gonderme kodu calismadi:",text)   
            except:
                logging.error("Message sender hatasi")

"""
# Usage example
if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
    CHAT_ID = 'your_chat_id'
    message_sender = TelegramMessageSender(TELEGRAM_BOT_TOKEN, CHAT_ID)
    response = message_sender.send_message("Hello, this is a test message!")
    print(response)
"""