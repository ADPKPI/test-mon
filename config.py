response_time_limit = 1
resourse_limits = {
    "CPU":75,
    "RAM":75,
    "DISK SPACE":75
}

servers = [
    {
        "name": "DB-master",
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
        "name": "DB-slave",
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
        "name": "TG1",
        "host": "78.140.189.246",
        "user": "root",
        "password":"5q9fAM56B5iBL7wsoN",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "service", "name": "Client Bot", "service":"adp-client-bot.service"},
            {"type": "service", "name": "Shop Bot", "service":"adp-shop-bot.service"},
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
            {"type": "service", "name": "Backup Service", "service": "backup.service"},
            {"type": "service", "name": "CRON", "service": "cron.service"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    }
]

chats = [684172842]
