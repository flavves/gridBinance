import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from TelegramMessageSender import TelegramMessageSender
from unittest.mock import patch

@pytest.fixture
def telegram_sender():
    bot_token = "test_telegram_bot_token"
    chat_id = "test_chat_id"
    return TelegramMessageSender(bot_token, chat_id)

@patch("requests.post")
def test_send_message(mock_post, telegram_sender):
    mock_post.return_value.status_code = 200
    response = telegram_sender.send_message("Test message")
    assert response == "Message sent successfully"
    mock_post.assert_called_once()