import json
import os

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # баштапкы маалыматтар
        from config import DEFAULT_DATA
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_link(key):
    data = load_data()
    return data["links"].get(key, "")

def set_link(key, value):
    data = load_data()
    data["links"][key] = value
    save_data(data)

def get_promocode(key):
    data = load_data()
    return data["promocodes"].get(key, "")

def set_promocode(key, value):
    data = load_data()
    data["promocodes"][key] = value
    save_data(data)