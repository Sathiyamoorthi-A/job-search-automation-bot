import requests
import time
import urllib.parse
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message_text: str, parse_mode: str = "HTML") -> bool:
    """Sends a raw message to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram Warning] Bot Token or Chat ID not configured.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"[Telegram Error] HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[Telegram Exception] {e}")
        return False

def test_telegram_connection() -> bool:
    """Sends a test ping to verify Telegram Bot setup."""
    text = (
        "🚀 <b>Job Alert Bot Connected!</b>\n\n"
        "Hello <b>Sathiyamoorthi</b>! Your automated Java Full Stack daily job radar is now active.\n"
        "You will receive newly posted matching jobs here automatically."
    )
    return send_telegram_message(text)

def escape_html(text: str) -> str:
    """Safely escapes HTML special characters."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def send_job_alert(job: dict) -> bool:
    """Sends a formatted job card to Telegram."""
    title = escape_html(job.get("title", "Software Developer"))
    company = escape_html(job.get("company", "Company"))
    location = escape_html(job.get("location", "India"))
    source = escape_html(job.get("source", "LinkedIn"))
    apply_url = job.get("url", "")
    time_posted = escape_html(job.get("time_posted", "Recently"))

    message = (
        f"🎯 <b>NEW JOB MATCH</b>\n\n"
        f"💼 <b>Role:</b> {title}\n"
        f"🏢 <b>Company:</b> {company}\n"
        f"📍 <b>Location:</b> {location}\n"
        f"🕒 <b>Posted:</b> {time_posted}\n"
        f"🌐 <b>Source:</b> {source}\n\n"
        f"👉 <a href=\"{apply_url}\"><b>[ Click Here to Apply ]</b></a>"
    )
    
    success = send_telegram_message(message)
    if success:
        time.sleep(0.5)  # Telegram API rate limit protection
    return success

def send_daily_summary(total_found: int, total_sent: int):
    """Sends a final summary report after scraping run."""
    text = (
        f"📊 <b>Daily Job Search Complete</b>\n\n"
        f"🔍 Total Matching Roles Scanned: <b>{total_found}</b>\n"
        f"✨ New Alerts Delivered: <b>{total_sent}</b>\n\n"
        f"<i>Targeting: Java | Spring Boot | React | MySQL (1-3 Yrs Exp)</i>"
    )
    send_telegram_message(text)
