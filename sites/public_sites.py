from utils import get_last_notice, save_last_notice, send_telegram_alert

def monitor_public_site(page, site_name, site_config):
    url = site_config["url"]
    selector = site_config["selector"]
    cache_file = site_config["cache_file"]

    print(f"[{site_name}] Navigating to {url}...")
    page.goto(url, timeout=30000, wait_until="domcontentloaded")

    try:
        page.wait_for_selector(selector, timeout=15000)
        latest_text = page.locator(selector).inner_text().strip()
        print(f"[{site_name} Result] Found: '{latest_text}'")

        previous_text = get_last_notice(cache_file)

        if latest_text and latest_text != previous_text:
            send_telegram_alert(site_name, latest_text)
            save_last_notice(cache_file, latest_text)
        else:
            print(f"[{site_name}] No updates detected.")

    except Exception as e:
        print(f"[{site_name} Failure] Could not locate announcement element: {e}")