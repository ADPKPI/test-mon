from abc import ABC, abstractmethod
import subprocess
import socket
import requests
import os
import psutil
import telnetlib
import time
import paramiko


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
            with telnetlib.Telnet(self.host, self.port, timeout=10) as tn:
                # Просто устанавливаем соединение, без ожидания конкретного ответа
                return True
        except Exception as e:
            print(f"Error connecting to {self.host}:{self.port}: {e}")
            return False

    def response_time(self) -> float:
        try:
            start_time = time.time()
            with telnetlib.Telnet(self.host, self.port, timeout=10) as tn:
                end_time = time.time()
                return end_time - start_time
        except Exception as e:
            end_time = time.time()
            print(f"Failed to connect to {self.host}:{self.port}: {e}")
            return end_time - start_time


class ScriptMonitor(IMonitorStrategy):
    """
       Проверка активности Python скрипта на удаленном сервере через SSH.
       """

    def __init__(self, hostname, port, username, password, script_name):
        """
        Инициализация монитора.
        :param hostname: Имя хоста или IP адрес удаленного сервера.
        :param port: Порт SSH.
        :param username: Имя пользователя для SSH соединения.
        :param password: Пароль пользователя для SSH соединения.
        :param script_name: Имя скрипта для мониторинга.
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.script_name = script_name

    def check(self) -> bool:
        """
        Выполняет проверку активности скрипта на удаленном сервере.
        :return: True, если скрипт активен, иначе False.
        """
        command = f"ps aux | grep python | grep -v grep | grep {self.script_name}"
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.readlines()
            ssh.close()

            return len(output) > 0
        except Exception as e:
            print(f"Ошибка при подключении или выполнении команды на сервере: {e}")
            return False


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

# Пример использования
hostname = '78.140.162.131'
port = 22
username = 'root'
password = '0C4k9p3l9OZiTnFrM3'
script_name = 'main.py'

monitor = ScriptMonitor(hostname, port, username, password, script_name)
is_active = monitor.check()
print(f"Скрипт активен: {is_active}")


