import time
import requests
from playwright.sync_api import sync_playwright

# Ensure your ac'tual credentials are here
TELEGRAM_TOKEN ="Your Token"
CHAT_ID = "Your Chat ID"

MONITORED_SITES = [
    {
        "name": "Audit & Compliance Portal",
        "url": "https://chic-marzipan-f94621.netlify.app/",
        "selector": "#notif-count",  # Change to '#notif-1-title' if you want to track the headline instead
        "last_state": None
    }
]

def send_telegram_alert(site_name, url, change_text):
    message = f"🚨 Audit Alert Update!\n\nWebsite: {site_name}\nURL: {url}\n\nNew Value: {change_text}"
    endpoint = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(endpoint, data=payload)
        res_json = response.json()
        if res_json.get("ok"):
            print(f"[Telegram Success] Alert delivered!")
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

            if site["last_state"] is None:
                site["last_state"] = current_text
                print(f"[{site['name']}] Initial state saved: '{current_text}'")
            elif current_text != site["last_state"]:
                print(f"[{site['name']}] Change detected! Old: '{site['last_state']}' | New: '{current_text}'")
                send_telegram_alert(site["name"], site["url"], current_text)
                site["last_state"] = current_text
            else:
                print(f"[{site['name']}] No changes detected.")
                
        except Exception as e:
            print(f"Error checking {site['name']}: {e}")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as p:
        print("Starting Audit Portal monitoring...")
        while True:
            check_sites(p)
            time.sleep(10)  # Sleep interval between checks