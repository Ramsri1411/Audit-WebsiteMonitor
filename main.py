from playwright.sync_api import sync_playwright
from config import PUBLIC_SITES
from sites.netlify import monitor_netlify
from sites.public_sites import monitor_public_site

def run_all_monitors():
    with sync_playwright() as p:
        # User-Agent prevents anti-bot blocks on public sites
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 1. Run Netlify Private Portal Monitor
        try:
            monitor_netlify(page)
        except Exception as e:
            print(f"[Netlify Execution Failure]: {e}")

        # 2. Run Public Portal Monitors (ICAI, RBI, PIB)
        for site_name, site_config in PUBLIC_SITES.items():
            try:
                monitor_public_site(page, site_name, site_config)
            except Exception as e:
                print(f"[{site_name} Execution Failure]: {e}")

        browser.close()

if __name__ == "__main__":
    run_all_monitors()