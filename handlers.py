from dotenv import load_dotenv
from telegram import Bot
import logging
import os
from config import chats
import asyncio

class FailureHandlingStrategy:
    def handle(self, server_name, check_name, error):
        pass
class StrategyFactory:
    def __init__(self):
        self.notify_strategy = NotifyStrategy()
    def get_strategy(self, server_name, check_name, other_checks):
        return self.notify_strategy

class NotifyStrategy(FailureHandlingStrategy):
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("MON_BOT_TOKEN")
        self.bot = Bot(token=self.bot_token)

    async def handle(self, server_name, check_name):
        try:
            for id in chats:
                await self.bot.send_message(chat_id=id, text=f"ТРЕВОГААААААААААААААААААААААААААААААААААААА {server_name} - {check_name} НАЕБНУЛСЯ!!!")
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")
