import requests
import time
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
        "🚀 <b>Direct HR Job Radar Connected!</b>\n\n"
        "Hello <b>Sathiyamoorthi</b>! Filtered for <b>Direct Corporate HR Postings</b>.\n"
        "Third-party staffing agency reposts are filtered out."
    )
    return send_telegram_message(text)

def escape_html(text: str) -> str:
    """Safely escapes HTML special characters."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def calculate_apply_urgency(time_posted: str) -> tuple:
    """Analyzes posting age and calculates optimal recruiter application timing status."""
    tp_lower = time_posted.lower()
    
    if any(k in tp_lower for k in ["minute", "min", "just now", "1 hour", "2 hour", "3 hour", "new"]):
        return (
            "⚡ <b>GOLDEN APPLY WINDOW (DIRECT HR)</b>",
            "🔥 <i>Apply immediately to the direct hiring team before ATS volume builds up!</i>"
        )
    elif any(k in tp_lower for k in ["hour", "today"]):
        return (
            "🟢 <b>FRESH DIRECT REQUISITION</b>",
            "🚀 <i>Direct corporate posting! High recruiter visibility window.</i>"
        )
    else:
        return (
            "🏢 <b>DIRECT COMPANY POSTING</b>",
            "💡 <i>Direct company career portal requisition.</i>"
        )

def send_job_alert(job: dict) -> bool:
    """Sends a formatted job card with direct HR portal badge to Telegram."""
    title = escape_html(job.get("title", "Software Developer"))
    company = escape_html(job.get("company", "Company"))
    location = escape_html(job.get("location", "India"))
    source = escape_html(job.get("source", "Direct Career Portal"))
    apply_url = job.get("url", "")
    time_posted = escape_html(job.get("time_posted", "Recently"))
    hr_email = escape_html(job.get("hr_email", ""))
    is_direct_ats = job.get("is_direct_ats", False)

    badge, timing_tip = calculate_apply_urgency(time_posted)

    ats_badge = "🌐 <b>Direct ATS Career Portal (Greenhouse/Lever/Workday/Ashby)</b>\n" if is_direct_ats else ""
    email_section = f"\n📧 <b>Direct HR Email:</b> <a href=\"mailto:{hr_email}\"><code>{hr_email}</code></a>\n" if hr_email else ""

    message = (
        f"{badge}\n\n"
        f"💼 <b>Role:</b> {title}\n"
        f"🏢 <b>Company:</b> {company}\n"
        f"📍 <b>Location:</b> {location}\n"
        f"🕒 <b>Posted:</b> {time_posted}\n"
        f"🌐 <b>Source:</b> {source}\n"
        f"{ats_badge}"
        f"{email_section}\n"
        f"{timing_tip}\n\n"
        f"👉 <a href=\"{apply_url}\"><b>[ Apply Directly on Company Portal ]</b></a>"
    )
    
    success = send_telegram_message(message)
    if success:
        time.sleep(0.5)
    return success

def send_daily_summary(total_found: int, total_sent: int, scan_slot: str = "Daily"):
    """Sends a final summary report after scraping run."""
    text = (
        f"📊 <b>Direct HR Job Scan Complete ({scan_slot})</b>\n\n"
        f"🏢 Direct Company Openings Scanned: <b>{total_found}</b>\n"
        f"✨ New Direct HR Alerts Delivered: <b>{total_sent}</b>\n\n"
        f"🛡️ <i>Note: All 3rd-party staffing agency reposts & ghost listings are automatically filtered out.</i>"
    )
    send_telegram_message(text)
