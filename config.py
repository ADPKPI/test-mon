servers = [
    {
        "name": "DB-master1",
        "host": "78.140.189.245",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "DB-master2",
        "host": "206.54.191.53",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "DB-slave1",
        "host": "206.54.170.119",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "DB-slave2",
        "host": "206.54.191.62",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "TG1",
        "host": "78.140.189.246",
        "user": "root",
        "password":"5q9fAM56B5iBL7wsoN",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "script", "name": "Bot", "script": "initialization.py"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "BACKUPS",
        "host": "78.140.162.131",
        "user": "root",
        "password": "0C4k9p3l9OZiTnFrM3",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "script", "name": "Backup Service", "script": "main.py"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    }
]
