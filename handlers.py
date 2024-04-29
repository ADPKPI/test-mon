import aioredis

REDIS_URL = "redis://localhost"

class FailureHandlingStrategy:
    def handle(self, server_name, check_name):
        pass
class StrategyFactory:
    def __init__(self):
        self.notify_strategy = NotifyStrategy()
    def get_strategy(self, server_name, check_name, other_checks):
        return self.notify_strategy

class NotifyStrategy(FailureHandlingStrategy):
    async def handle(self, server_name, check_name):
        redis = await aioredis.create_redis_pool(REDIS_URL)
        message = (123456789, f"ТРЕВОГА: сервер {server_name} недоступен!")
        await redis.rpush("telegram_queue", str(message))


