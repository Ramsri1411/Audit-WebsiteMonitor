# Automated Audit & Compliance Web Monitor

Playwright checks a protected portal on a schedule, signs in with credentials from environment secrets, and sends a Telegram alert when the notification count rises.

## Authenticated monitoring

Set these GitHub Actions secrets (or local environment variables):

- `TELEGRAM_TOKEN`
- `CHAT_ID`
- `SITE_USERNAME` — demo value: `audit.admin`
- `SITE_PASSWORD` — demo value: `Compliance2026!`

The crawler:

1. Reuses a saved Playwright session from `sessions/` when it is still valid.
2. Otherwise fills username and password.
3. On **this** demo portal, reads the on-screen challenge text and types it into the challenge field.
4. Opens the regulatory feed and reads `#notif-count`.

Redeploy `index.html` to Netlify after pulling these changes, or the live site will still be unauthenticated.

## Third-party sites (banks, government portals, etc.)

You may store **your own** username and password and point `auth` selectors at that site's login form.

This project will **not** automatically solve third-party anti-bot CAPTCHAs (Google reCAPTCHA, hCaptcha, image puzzles, or paid solver APIs). Those controls exist to block bots, including this one.

For those sites, log in once in a headed browser, save `storage_state`, and let the monitor reuse cookies until they expire. When a third-party CAPTCHA appears, the job fails with instructions to refresh the session instead of trying to bypass it.

## Local run

```bash
pip install -r requirements.txt
playwright install chromium
set SITE_USERNAME=audit.admin
set SITE_PASSWORD=Compliance2026!
python monitor.py
```
