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
    loop.run_until_complete(dp.start_polling(bot, handle_signals=False))

if __name__ == "__main__":
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
