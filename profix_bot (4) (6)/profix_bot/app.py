import asyncio
import os
import logging
import threading
from flask import Flask
from main import bot, dp

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!", 200


def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner():
        while True:
            try:
                await dp.start_polling(bot, handle_signals=False)
            except Exception as e:
                logging.error(f"Polling crashed: {e}")
            await asyncio.sleep(5)

    loop.run_until_complete(runner())


# gunicorn менен да, python app.py менен да бот бир жолу гана башталат
_started = False


def start_bot_thread():
    global _started
    if not _started:
        _started = True
        threading.Thread(target=run_bot, daemon=True).start()


start_bot_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
