from bot import send_message_to_chats
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
        await send_message_to_chats(f"ТРЕВОГААААААААААААААААААААААААААА\n{server_name} наебнулся")


