import json
import os

def load_json(path,fallback_value=None):
    if fallback_value is None:
        fallback_value = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}, returning fallback value")
        return fallback_value

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

