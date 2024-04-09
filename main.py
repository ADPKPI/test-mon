from abc import ABC, abstractmethod
import subprocess
import socket
import requests
import os
import psutil
import telnetlib
import time


class IMonitorStrategy(ABC):
    """
    Интерфейс стратегии мониторинга
    """
    @abstractmethod
    def check(self) -> bool:
        pass

    @abstractmethod
    def response_time(self) -> float:
        pass

class ServerPingMonitor(IMonitorStrategy):
    """
    Мониторинг сервера через ping
    """
    def __init__(self, host):
        self.host = host

    def check(self) -> bool:
        response = subprocess.run(['ping', '-c', '1', self.host], stdout=subprocess.PIPE)
        return response.returncode == 0

    def response_time(self) -> float:
        response = subprocess.run(['ping', '-c', '1', self.host], stdout=subprocess.PIPE)
        output = response.stdout.decode('cp1251')
        time_pos = output.find('time=')
        if time_pos != -1:
            start = time_pos + 5
            end = output.find(' ', start)
            return float(output[start:end])
        return -1.0

class TelnetMonitor:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def check(self) -> bool:
        try:
            with telnetlib.Telnet(self.host, self.port) as tn:
                # Просто устанавливаем соединение, без ожидания конкретного ответа
                return True
        except Exception as e:
            print(f"Error connecting to {self.host}:{self.port}: {e}")
            return False

    def response_time(self) -> float:
        try:
            start_time = time.time()
            with telnetlib.Telnet(self.host, self.port) as tn:
                end_time = time.time()
                return end_time - start_time
        except Exception as e:
            end_time = time.time()
            print(f"Failed to connect to {self.host}:{self.port}: {e}")
            return end_time - start_time

class APIMonitor(IMonitorStrategy):
    """
    Мониторинг доступности API по определенному порту
    """
    # Реализация опущена для краткости

class ScriptMonitor(IMonitorStrategy):
    """
    Проверка активности Python скрипта на сервере
    """
    # Реализация опущена для краткости

class TelegramBotMonitor(IMonitorStrategy):
    """
    Проверка работоспособности телеграм бота
    """
    # Реализация опущена для краткости

class Monitor:
    """
    Класс мониторинга, использующий различные стратегии
    """
    def __init__(self, strategy: IMonitorStrategy):
        self.strategy = strategy

    def check_availability(self) -> bool:
        return self.strategy.check()

    def check_response_time(self) -> float:
        return self.strategy.response_time()

telnet = TelnetMonitor('78.140.189.245', 3306)
print(telnet.check())
print(telnet.response_time())


