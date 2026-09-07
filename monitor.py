import os
import requests
from playwright.sync_api import sync_playwright

# Fetch credentials from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MONITORED_SITES = [
    {
        "name": "Audit & Compliance Portal",
        "url": "https://chic-marzipan-f94621.netlify.app/",
        "selector": "#notif-count"
    }
]

def send_telegram_alert(site_name, url, change_text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[Error] Missing Telegram credentials in environment variables.")
        return

    message = f"🚨 Audit Alert Update!\n\nWebsite: {site_name}\nURL: {url}\n\nNew Value: {change_text}"
    endpoint = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    
    try:
        response = requests.post(endpoint, data=payload)
        res_json = response.json()
        if res_json.get("ok"):
            print("[Telegram Success] Alert delivered!")
        else:
            print(f"[Telegram Error] {res_json.get('description')}")
    except Exception as e:
        print(f"[Network Error] {e}")

def check_sites(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    for site in MONITORED_SITES:
        try:
            page.goto(site["url"], timeout=15000)
            page.wait_for_selector(site["selector"], timeout=10000)
            current_text = page.locator(site["selector"]).inner_text().strip()
            
            print(f"[{site['name']}] Current selector value: '{current_text}'")
            
            # Send alert if count exceeds base baseline (or modify logic as needed)
            if int(current_text) > 5:
                send_telegram_alert(site["name"], site["url"], current_text)

        except Exception as e:
            print(f"Error checking {site['name']}: {e}")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as p:
        print("Executing scheduled site check via GitHub Actions...")
        check_sites(p)
