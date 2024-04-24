#!/usr/bin/python3

from abc import ABC, abstractmethod
import subprocess
import socket
import requests
import os
import psutil
import telnetlib
import time
import paramiko
from config import servers, resourse_limits, response_time_limit
from threading import Thread
from multiprocessing import Process
import logging
import json
from datetime import datetime
from api import app
from handlers import StrategyFactory
import asyncio



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

class TelnetMonitor(IMonitorStrategy):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def check(self) -> bool:
        try:
            with telnetlib.Telnet(self.host, self.port, timeout=10) as tn:
                # Просто устанавливаем соединение, без ожидания конкретного ответа
                return True
        except Exception as e:
            logging.error(f"Error connecting to {self.host}:{self.port}: {e}")
            return False

    def response_time(self) -> float:
        try:
            start_time = time.time()
            with telnetlib.Telnet(self.host, self.port, timeout=10) as tn:
                end_time = time.time()
                return end_time - start_time
        except Exception as e:
            end_time = time.time()
            logging.error(f"Failed to connect to {self.host}:{self.port}: {e}")
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
            logging.error(f"Ошибка при подключении или выполнении команды на сервере: {e}")
            return False

    def response_time(self) -> float:
        return 0


class CPUMonitor(IMonitorStrategy):
    def check(self) -> bool:
        # В данном случае `check` может возвращать True, если удалось получить данные
        return True

    def response_time(self) -> float:
        # Получаем среднюю загрузку CPU за последнюю минуту
        load1, _, _ = psutil.getloadavg()
        cpu_usage = (load1 / psutil.cpu_count()) * 100
        return cpu_usage

class RAMMonitor(IMonitorStrategy):
    def check(self) -> bool:
        # Аналогично, возвращает True, если получение информации об успешном
        return True

    def response_time(self) -> float:
        # Использование оперативной памяти в процентах
        mem = psutil.virtual_memory()
        return mem.percent

class DiskMonitor(IMonitorStrategy):
    def __init__(self, disk='/'):
        self.disk = disk

    def check(self) -> bool:
        # Возвращает True, если удалось получить информацию о диске
        return True

    def response_time(self) -> float:
        # Использование дискового пространства в процентах для указанного раздела
        usage = psutil.disk_usage(self.disk)
        return usage.percent


class CheckManager:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.handlers = StrategyFactory()
        self.aggregate_results = {}
        self.threads = []

    def run_check(self, server, check):
        host = server.get("host")
        check_name = check.get("name")
        try:
            if check['type'] == 'ping':
                monitor = ServerPingMonitor(host)
            elif check['type'] == 'telnet':
                monitor = TelnetMonitor(host, check['port'])
            elif check['type'] == 'script':
                monitor = ScriptMonitor(host, 22, server['user'], server['password'], check['script'])
            elif check['type'] == 'cpu':
                monitor = CPUMonitor()
            elif check['type'] == 'ram':
                monitor = RAMMonitor()
            elif check['type'] == 'disk_space':
                monitor = DiskMonitor()
            else:
                return

            result = monitor.check()
            response_time = monitor.response_time()
            self.log_result(server["name"], check["name"], result, response_time)
            if check['type'] not in 'cpu ram disk_space':
                if not result:
                    self.handle_failure(server["name"], check["name"])
                elif response_time >= response_time_limit:
                    self.handle_warning(server["name"], check["name"], response_time)
            elif check['type'] in 'cpu ram disk_space' and response_time >= resourse_limits[check_name]:
                self.handle_failure(server["name"], check["name"])
        except Exception as e:
            logging.error(e)

    def log_result(self, server_name, check_name, result, response_time=None):
        logger = logging.getLogger(server_name)
        if not logger.handlers:
            handler = logging.FileHandler(f"logs/{server_name}_checks.log")
            handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S'))
            logger.addHandler(handler)

        if (check_name in ["CPU", "RAM", "DISK SPACE"]):
            logger.info(
                f"{server_name} --- {check_name} --- {'Success' if result else 'Failure'} | {f'Usage: {round(response_time, 3)}%' if response_time is not None else ''}")
        else:
            logger.info(
                f"{server_name} --- {check_name} --- {'Success' if result else 'Failure'} | {f' Response Time: {round(response_time, 3)} seconds' if response_time is not None else ''}")
        if server_name not in self.aggregate_results:
            self.aggregate_results[server_name] = []
        self.aggregate_results[server_name].append({
            "check_name": check_name,
            "result": 'Success' if result else 'Failure',
            "response_time": round(response_time, 3) if response_time is not None else None,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    def handle_failure(self, server_name, check_name):
        with open('aggregate_results.json', 'r') as file:
            data = json.load(file)
        handler = self.handlers.get_strategy(server_name, check_name, data)
        asyncio.run(handler.handle(server_name, check_name))

    def handle_warning(self, server_name, check_name, value):
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def save_aggregate_results(self):
        with open("aggregate_results.json", "w") as json_file:
            json_str = json.dumps(self.aggregate_results, indent=4)
            json_file.write(json_str)

    def start(self):
        while True:
            for server in servers:
                for check in server['checks']:
                    thread = Thread(target=self.run_check, args=(server, check,))
                    self.threads.append(thread)
                    thread.start()

            for thread in self.threads:
                thread.join()  # Ensure all threads have completed

            self.save_aggregate_results()
            self.threads = []  # Reset the thread list for the next cycle
            time.sleep(60)  # Wait for 1 minute before next round of checks

def start_monitoring():
    manager = CheckManager()
    manager.start()

if __name__ == "__main__":
    start_monitoring()