import io
import os
import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

# Local Windows Tesseract Executable Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Credentials & Configurations (Uses System Environment Variables or Local Fallbacks)
USERNAME = os.getenv("SITE_USERNAME", "auditor")
PASSWORD = os.getenv("SITE_PASSWORD", "audit2026")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8612323305:AAFWdWUUAEaMm8MU0oLwEg83c3xNFd5uSqw")
CHAT_ID = os.getenv("CHAT_ID", "1417372406")

TARGET_URL = "https://frabjous-treacle-fc1e28.netlify.app/"
LAST_NOTICE_FILE = "last_notice.txt"

# Inspected Target Elements
SELECTORS = {
    "username": "#username",
    "password": "#password",
    "captcha_canvas": "#captcha-canvas",
    "captcha_input": "#captcha",
    "login_btn": 'button[type="submit"]',
    "notif_count": "#notices > article:nth-child(1) > p"
}


def get_last_notice():
    """Reads the previously recorded notice text from disk."""
    if os.path.exists(LAST_NOTICE_FILE):
        with open(LAST_NOTICE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_last_notice(text):
    """Saves the latest notice text to disk to prevent duplicate alerts."""
    with open(LAST_NOTICE_FILE, "w", encoding="utf-8") as f:
        f.write(text)


def send_telegram_alert(notice_text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[Telegram Warning] TELEGRAM_TOKEN or CHAT_ID is not configured.")
        return

    message = f"🚨 New Portal Notice Detected!\n\n{notice_text}"
    endpoint = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    try:
        res = requests.post(endpoint, data=payload)
        if res.json().get("ok"):
            print("[Telegram Alert] Alert sent successfully!")
        else:
            print(f"[Telegram Error] API returned: {res.json().get('description')}")
    except Exception as e:
        print(f"[Network Error] Failed to send Telegram alert: {e}")


def solve_canvas_captcha(page):
    print("[OCR] Extracting CAPTCHA image from canvas...")
    canvas = page.wait_for_selector(SELECTORS["captcha_canvas"], timeout=10000)
    image_bytes = canvas.screenshot()

    # Convert bytes to PIL Image and then NumPy array for OpenCV
    image = Image.open(io.BytesIO(image_bytes))
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    # Thresholding to enhance text clarity against noise lines
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    cv2.imwrite("captcha_debug.png", thresh)

    # Whitelist OCR for alphanumeric CAPTCHA characters
    ocr_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw_text = pytesseract.image_to_string(thresh, config=ocr_config)
    cleaned_code = raw_text.strip().replace(" ", "")

    print(f"[OCR Output] Recognized CAPTCHA Code: '{cleaned_code}'")
    return cleaned_code


def run_monitor(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        print("[1/3] Navigating to portal...")
        page.goto(TARGET_URL, timeout=30000)

        max_attempts = 5
        logged_in = False

        for attempt in range(1, max_attempts + 1):
            print(f"[2/3] Login Attempt {attempt}/{max_attempts}...")

            # Refill fields
            page.fill(SELECTORS["username"], USERNAME)
            page.fill(SELECTORS["password"], PASSWORD)

            captcha_code = solve_canvas_captcha(page)
            page.fill(SELECTORS["captcha_input"], captcha_code)

            print("Submitting login form...")
            page.click(SELECTORS["login_btn"])
            page.wait_for_timeout(2000)  # Brief delay to allow error check or redirect

            # Check if CAPTCHA error message appeared
            error_locator = page.locator("text=Captcha did not match")
            if error_locator.count() > 0 and error_locator.is_visible():
                print("[OCR Retry] CAPTCHA was misread. Retrying with new CAPTCHA...")
                continue
            else:
                logged_in = True
                break

        if not logged_in:
            raise Exception("Failed to log in after maximum CAPTCHA retries.")

        print("[3/3] Checking dashboard for updates...")
        page.wait_for_selector(SELECTORS["notif_count"], timeout=30000)

        latest_notice = page.locator(SELECTORS["notif_count"]).inner_text().strip()
        print(f"[Result] Latest Notice Content:\n'{latest_notice}'")

        previous_notice = get_last_notice()

        # Alert ONLY if notice text exists AND is different from the stored notice
        if latest_notice and latest_notice != previous_notice:
            print("[Alert] New notice detected! Dispatching Telegram notification...")
            send_telegram_alert(latest_notice)
            save_last_notice(latest_notice)
        else:
            print("[No Action] Notice content is identical to the last check. Skipping alert.")

    except Exception as e:
        print(f"[Execution Failure] Monitoring process failed: {e}")
        page.screenshot(path="login_debug.png")
        print("[Debug] Saved failure screenshot to 'login_debug.png'")

    finally:
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        run_monitor(p)