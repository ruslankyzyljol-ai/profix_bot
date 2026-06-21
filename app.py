from flask import Flask
import threading
import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    from main import bot, dp
    loop.run_until_complete(dp.start_polling(bot))

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
