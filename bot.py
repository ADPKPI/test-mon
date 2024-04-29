import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv
from asyncio.queues import Queue
from config import chats

load_dotenv()
TOKEN = os.getenv("MON_BOT_TOKEN")
bot = Bot(TOKEN)
message_queue = Queue()

async def process_messages():
    while True:
        message = await message_queue.get()
        text = message
        for id in chats:
            await bot.send_message(chat_id=id, text=text)

async def main():
    task = asyncio.create_task(process_messages())
    await task

if __name__ == '__main__':
    asyncio.run(main())
