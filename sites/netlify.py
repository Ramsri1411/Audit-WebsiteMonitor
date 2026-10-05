import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
from config import TESSERACT_CMD, NETLIFY_CONFIG
from utils import get_last_notice, save_last_notice, send_telegram_alert

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def solve_canvas_captcha(page, selector):
    print("[Netlify OCR] Capturing canvas element...")
    canvas = page.wait_for_selector(selector, timeout=10000)
    image_bytes = canvas.screenshot()

    image = Image.open(io.BytesIO(image_bytes))
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    ocr_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw_text = pytesseract.image_to_string(thresh, config=ocr_config)
    return raw_text.strip().replace(" ", "")

def monitor_netlify(page):
    cfg = NETLIFY_CONFIG
    sel = cfg["selectors"]

    print("[Netlify] Navigating to portal...")
    page.goto(cfg["url"], timeout=30000)

    max_attempts = 5
    logged_in = False

    for attempt in range(1, max_attempts + 1):
        print(f"[Netlify] Login attempt {attempt}/{max_attempts}...")
        page.fill(sel["username"], cfg["username"])
        page.fill(sel["password"], cfg["password"])

        code = solve_canvas_captcha(page, sel["captcha_canvas"])
        page.fill(sel["captcha_input"], code)
        page.click(sel["login_btn"])
        page.wait_for_timeout(2000)

        if page.locator("text=Captcha did not match").is_visible():
            print("[Netlify OCR] Misread code. Retrying...")
            continue
        else:
            logged_in = True
            break

    if not logged_in:
        raise Exception("Failed to log in to Netlify after retries.")

    page.wait_for_selector(sel["notif_count"], timeout=30000)
    latest = page.locator(sel["notif_count"]).inner_text().strip()
    previous = get_last_notice(cfg["cache_file"])

    if latest and latest != previous:
        send_telegram_alert("Netlify Portal", latest)
        save_last_notice(cfg["cache_file"], latest)
    else:
        print("[Netlify] No new notices detected.")