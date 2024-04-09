servers = [
    {
        "name": "DB-master1",
        "host": "78.140.189.245",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22}
        ]
    },
    {
        "name": "DB-master2",
        "host": "206.54.191.53",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22}
        ]
    },
    {
        "name": "DB-slave1",
        "host": "206.54.170.119",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22}
        ]
    },
    {
        "name": "DB-slave2",
        "host": "206.54.191.62",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22}
        ]
    }
]
