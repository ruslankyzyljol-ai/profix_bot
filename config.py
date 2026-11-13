import os
import json
import logging

# Токен: BOT_TOKEN же TELEGRAM_TOKEN - экөөнүн бири Render Environment'те болсо жетет
BOT_TOKEN = (os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN") or "").strip()

try:
    ADMIN_ID = int((os.environ.get("ADMIN_ID") or "0").strip())
except ValueError:
    ADMIN_ID = 0

CHANNEL_USERNAME = "@profixkg"
CHANNEL_URL = "https://t.me/profixkg"

MINES_DIR = "images"

LINKS = {
    "1win": "https://one-vv0073.com/?p=hors",
    "mostbet": "https://r7ycnmimb.com/K9mU"
}

PROMOS = {
    "1win": "PROFIN",
    "mostbet": "PROFIX"
}

# ==================== САКТОО (кайра иштегенде өчпөсүн үчүн) ====================
# Render Disk кошсоңуз, DATA_DIR=/data деп Environment'ке жазыңыз.
DATA_DIR = os.environ.get("DATA_DIR", "data")
DATA_FILE = os.path.join(DATA_DIR, "data.json")

USER_LANG = {}


def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            LINKS.update(data.get("links", {}))
            PROMOS.update(data.get("promos", {}))
            for k, v in data.get("user_lang", {}).items():
                USER_LANG[int(k)] = v
    except Exception as e:
        logging.error(f"load_data error: {e}")


def save_data():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                {"links": LINKS, "promos": PROMOS,
                 "user_lang": {str(k): v for k, v in USER_LANG.items()}},
                f, ensure_ascii=False
            )
        os.replace(tmp, DATA_FILE)
    except Exception as e:
        logging.error(f"save_data error: {e}")


load_data()
