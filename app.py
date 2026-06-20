from flask import Flask
import threading
import asyncio
import os
import logging

# main.py ден ботту импорттойбуз
from main import bot, dp

# Логинг
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Ботту иштетүү"""
    logging.info("Бот ишке кирди!")
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    # Ботту өзүнчө агымда иштетебиз
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Flask серверин иштетебиз (Render порт талап кылат)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)