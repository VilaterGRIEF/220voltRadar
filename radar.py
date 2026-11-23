
import os
import json
import socket
import urllib.request
import urllib.parse

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = os.environ["ADMIN_ID"]

SERVERS = {
    "🇩🇪 Германия": ("159.200.230.212", 25321),
    "🇳🇱 Нидерланды TCP": ("79.182.70.186", 26021),
    "🇳🇱 Нидерланды gRPC": ("79.182.70.186", 26022),
    "🇳🇱 Нидерланды XHTTP": ("79.182.70.186", 26023),
}

STATE_FILE = "status.json"


def check(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except OSError:
        return False


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": ADMIN_ID,
        "text": text
    }).encode()

    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=15) as response:
        response.read()


def main():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            old = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        old = None

    current = {}

    for name, (host, port) in SERVERS.items():
        current[name] = check(host, port)

    if old is not None:
        for name, online in current.items():
            if name in old and old[name] != online:
                status = "🟢 Сервер восстановлен" if online else "🔴 Сервер недоступен"
                send_message(f"{status}\n{name}")

    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(current, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
