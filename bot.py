import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import chats
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv("MON_BOT_TOKEN")

bot = Bot(TOKEN)

async def send_message_to_chats(message):
    for chat_id in chats:
        await bot.send_message(chat_id=chat_id, text=message)

async def main():
    await send_message_to_chats("Привет! Это тестовое сообщение.")

# Запускаем асинхронный цикл
if __name__ == '__main__':
    asyncio.run(main())
