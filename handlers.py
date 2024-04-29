import requests
from config import chats

class FailureHandlingStrategy:
    def handle(self, server_name, check_name):
        pass
class StrategyFactory:
    def __init__(self):
        self.notify_strategy = NotifyStrategy()
    def get_strategy(self, server_name, check_name, other_checks):
        return self.notify_strategy

class NotifyStrategy(FailureHandlingStrategy):
    def handle(self, server_name, check_name):
        url = 'http://127.0.0.1:5001/alert'
        for id in chats:
            data = {
                'chat_id': id,
                'message': f'Тревога: {server_name} не отвечает!'
            }
            response = requests.post(url, json=data)



