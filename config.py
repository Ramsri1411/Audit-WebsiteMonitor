import os
# config.py
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
# Telegram Credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8612323305:AAFWdWUUAEaMm8MU0oLwEg83c3xNFd5uSqw")
CHAT_ID = os.getenv("CHAT_ID", "1417372406")

# Tesseract Path
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Site Configurations
NETLIFY_CONFIG = {
    "url": "https://frabjous-treacle-fc1e28.netlify.app/",
    "username": os.getenv("SITE_USERNAME", "auditor"),
    "password": os.getenv("SITE_PASSWORD", "audit2026"),
    "cache_file": "last_netlify.txt",
    "selectors": {
        "username": "#username",
        "password": "#password",
        "captcha_canvas": "#captcha-canvas",
        "captcha_input": "#captcha",
        "login_btn": 'button[type="submit"]',
        "notif_count": "#notices > article:nth-child(1) > p"
    }
}

PUBLIC_SITES = {
    "ICAI": {
        "url": "https://www.icai.org/category/announcements",
        "selector": "body > div.container.mx-3 > div > ul > li:nth-child(1) > a",
        "cache_file": "last_icai.txt"
    },
    "RBI": {
        "url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
        "selector": "#doublescroll > table.tablebg > tbody > tr:nth-child(2) > td:nth-child(1) > a",
        "cache_file": "last_rbi.txt"
    },
    "PIB": {
        "url": "https://www.pib.gov.in/allRel.aspx?reg=48&lang=1",
        "selector": "#ContentPlaceHolder1_ulRelease > li:first-child > a",
        "cache_file": "last_pib.txt"
    }
}
