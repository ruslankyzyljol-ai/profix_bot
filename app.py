from flask import Flask
import asyncio
import os
import logging
import threading
from main import bot, dp

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(dp.start_polling(bot))
    except Exception as e:
        logging.error(f"Бот иштеп жатып ката: {e}")

if __name__ == "__main__":
    # Ботту өзүнчө агымда иштетүү
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
