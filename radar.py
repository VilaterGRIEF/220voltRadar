
import os
import socket
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

SERVERS = {
    "🇩🇪 Германия": ("159.200.230.212", 25321),
    "🇳🇱 Нидерланды TCP": ("79.182.70.186", 26021),
    "🇳🇱 Нидерланды gRPC": ("79.182.70.186", 26022),
    "🇳🇱 Нидерланды XHTTP": ("79.182.70.186", 26023),
}

previous = {}

def check(host, port):
    try:
        with socket.create_connection((host, port), timeout=4):
            return True
    except OSError:
        return False

async def status_text():
    lines = ["⚡ 220voltRadar — состояние серверов\n"]
    for name, (host, port) in SERVERS.items():
        ok = await asyncio.to_thread(check, host, port)
        previous[name] = ok
        lines.append(f"{name}: {'🟢 Онлайн' if ok else '🔴 Недоступен'}")
    lines.append(f"\n🕒 {datetime.now().strftime('%H:%M:%S')}")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ 220voltRadar\n\nМониторинг серверов 220voltVPN.\n"
        "Команда /status — проверить серверы."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(await status_text())

async def monitor(context: ContextTypes.DEFAULT_TYPE):
    for name, (host, port) in SERVERS.items():
        ok = await asyncio.to_thread(check, host, port)

        if name in previous and previous[name] != ok:
            message = (
                f"{'🟢 Восстановление' if ok else '🔴 Сбой'}\n"
                f"{name}\n"
                f"Адрес: {host}:{port}"
            )
            await context.bot.send_message(ADMIN_ID, message)

        previous[name] = ok

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    app.job_queue.run_repeating(monitor, interval=60, first=5)

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
