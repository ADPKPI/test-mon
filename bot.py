import asyncio
import aioredis
import os
from telegram import Bot
from dotenv import load_dotenv
from config import chats

load_dotenv()
TOKEN = os.getenv("MON_BOT_TOKEN")
bot = Bot(TOKEN)
REDIS_URL = "redis://localhost"  # Укажите URL вашего Redis сервера

async def process_messages(redis):
    while True:
        _, message = await redis.blpop("telegram_queue")
        text = eval(message)  # Используйте безопасное преобразование, если данные от внешних источников
        for id in chats:
            await bot.send_message(chat_id=id, text=text)


async def main():
    redis = await aioredis.create_redis_pool(REDIS_URL)
    await process_messages(redis)

if __name__ == '__main__':
    asyncio.run(main())
