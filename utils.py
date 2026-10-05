import os
import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def send_telegram_alert(site_name, notice_text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[Telegram Warning] Credentials missing.")
        return

    message = f"🚨 New Notice Detected on {site_name}!\n\n{notice_text}"
    endpoint = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    try:
        res = requests.post(endpoint, data=payload)
        if res.json().get("ok"):
            print(f"[{site_name}] Telegram alert dispatched successfully!")
        else:
            print(f"[{site_name} Error] API response: {res.json().get('description')}")
    except Exception as e:
        print(f"[{site_name} Error] Failed to send Telegram alert: {e}")

def get_last_notice(cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_last_notice(cache_file, text):
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(text)