from telegram import Bot
from telegram.error import TelegramError
from config import chats
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv("MON_BOT_TOKEN")

bot = Bot(TOKEN)

def send_message_to_chats(message):
    for chat_id in chats:
        bot.send_message(chat_id=chat_id, text=message)
