import requests
from config import chats

class FailureHandlingStrategy:
    def handle(self, server_name, check_name):
        pass
class StrategyFactory:
    def __init__(self):
        self.notify_failure_strategy = NotifyFailureStrategy()
        self.notify_warning_strategy = NotifyWarningStrategy()
    def get_strategy(self, server_name, check_type, other_checks):
        if(other_checks=='warning'):
            return self.notify_warning_strategy
        #if(check_type=='service' and other_checks[server_name][''])
        else:
            print(other_checks)
            return self.notify_failure_strategy

class NotifyFailureStrategy(FailureHandlingStrategy):
    def handle(self, server_name, check_name):
        url = 'http://127.0.0.1:5001/alert'
        for id in chats:
            data = {
                'chat_id': id,
                'message': f'Тревога: {server_name} --- {check_name} не отвечает!'
            }
            response = requests.post(url, json=data)

class NotifyWarningStrategy(FailureHandlingStrategy):
    def handle(self, server_name, check_name,value):
        url = 'http://127.0.0.1:5001/alert'
        for id in chats:
            data = {
                'chat_id': id,
                'message': f'Внимание! {server_name}: {check_name} = {value}'
            }
            response = requests.post(url, json=data)



