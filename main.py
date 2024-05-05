#!/usr/bin/python3

from abc import ABC, abstractmethod
import subprocess
import psutil
import telnetlib
import time
import paramiko
from config import servers, resourse_limits, response_time_limit
from threading import Thread
import logging
import json
from datetime import datetime
from handlers import StrategyFactory



class IMonitorStrategy(ABC):
    @abstractmethod
    def check(self) -> bool:
        pass

    @abstractmethod
    def response_time(self) -> float:
        pass

class ServerPingMonitor(IMonitorStrategy):
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


class ServiceMonitor(IMonitorStrategy):

    def __init__(self, hostname, port, username, password, service_name):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.service_name = service_name

    def check(self) -> bool:
        command = f"systemctl is-active {self.service_name}"
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            ssh.close()

            return output == 'active'
        except Exception as e:
            logging.error(f"Ошибка при подключении или выполнении команды на сервере: {e}")
            return False

    def response_time(self) -> float:
        return 0


class CPUMonitor(IMonitorStrategy):
    def check(self) -> bool:
        return True

    def response_time(self) -> float:
        load1, _, _ = psutil.getloadavg()
        cpu_usage = (load1 / psutil.cpu_count()) * 100
        return cpu_usage

class RAMMonitor(IMonitorStrategy):
    def check(self) -> bool:
        return True

    def response_time(self) -> float:
        mem = psutil.virtual_memory()
        return mem.percent

class DiskMonitor(IMonitorStrategy):
    def __init__(self, disk='/'):
        self.disk = disk

    def check(self) -> bool:
        return True

    def response_time(self) -> float:
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
            elif check['type'] == 'service':
                monitor = ServiceMonitor(host, 22, server['user'], server['password'], check['service'])
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
                    self.handle_failure(server["name"], check["name"], check['type'])
                elif response_time >= response_time_limit:
                    self.handle_warning(server["name"], check["name"], response_time)
            elif check['type'] in 'cpu ram disk_space' and response_time >= resourse_limits[check_name]:
                self.handle_warning(server["name"], check["name"], response_time)
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
        })

    def handle_failure(self, server_name, check_name, check_type):
        with open('./aggregate_results.json', 'r') as file:
            data = json.load(file)
        handler = self.handlers.get_strategy(server_name, check_type, data)
        handler.handle(server_name, check_name)

    def handle_warning(self, server_name, check_name, value):
        handler = self.handlers.get_strategy(server_name, check_name, 'warning')
        handler.handle(server_name, check_name, value)

    def save_aggregate_results(self):
        self.aggregate_results['last-check-time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("./aggregate_results.json", "w") as json_file:
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
                thread.join()

            self.save_aggregate_results()
            self.threads = []
            time.sleep(60)

def start_monitoring():
    manager = CheckManager()
    manager.start()

if __name__ == "__main__":
    start_monitoring()