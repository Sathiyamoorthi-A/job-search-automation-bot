import sys
import os
import argparse
from datetime import datetime

# Configure UTF-8 for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CANDIDATE_NAME
from storage import init_db, is_job_sent, mark_job_sent, get_stats
from scrapers import fetch_all_matching_jobs
from telegram_notifier import send_job_alert, send_daily_summary, test_telegram_connection

def save_to_markdown_report(new_jobs: list):
    """Saves newly discovered jobs into a readable markdown report."""
    report_file = os.path.join(os.path.dirname(__file__), "latest_jobs_report.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    lines = [
        f"# Job Radar Report - {CANDIDATE_NAME}",
        f"**Generated at:** {timestamp}",
        f"**Target Stack:** Java | Spring Boot | React JS | REST APIs | MySQL (1-3 Yrs Exp)\n",
        f"| # | Job Role | Company | Location | Source | Apply Link |",
        f"|---|----------|---------|----------|--------|------------|"
    ]
    
    for idx, job in enumerate(new_jobs, 1):
        title = job.get("title", "").replace("|", "-")
        company = job.get("company", "").replace("|", "-")
        loc = job.get("location", "").replace("|", "-")
        source = job.get("source", "Web")
        url = job.get("url", "#")
        lines.append(f"| {idx} | **{title}** | {company} | {loc} | {source} | [Apply Now]({url}) |")
        
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"[File] Local Markdown Report saved to: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Automated Job Alert Bot for Sathiyamoorthi")
    parser.add_argument("--test", action="store_true", help="Test Telegram Bot connection")
    args = parser.parse_args()

    # Step 1: Handle test flag
    if args.test:
        print("[Test] Testing Telegram Connection...")
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("[Error] Please configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env first.")
            sys.exit(1)
        ok = test_telegram_connection()
        if ok:
            print("[Success] Test message sent to your Telegram successfully!")
        else:
            print("[Error] Failed to send Telegram message. Please verify your Bot Token & Chat ID.")
        return

    # Step 2: Initialize Database
    init_db()
    
    telegram_enabled = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    if not telegram_enabled:
        print("[Info] Telegram credentials not set in .env. Output will be logged to console and saved to latest_jobs_report.md.")
        print("[Tip] To get instant phone alerts, add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")

    # Step 3: Fetch Matching Jobs
    jobs = fetch_all_matching_jobs()
    
    new_jobs = []
    sent_count = 0
    
    print("\n[Processing] Checking for new unseen jobs...")
    for job in jobs:
        url = job.get("url")
        if not is_job_sent(url):
            new_jobs.append(job)
            
            # If Telegram configured, send push alert
            if telegram_enabled:
                success = send_job_alert(job)
                if success:
                    mark_job_sent(url, job["title"], job["company"], job["location"], job["source"])
                    sent_count += 1
                    print(f"  + [Telegram Sent] {job['title']} @ {job['company']}")
                else:
                    print(f"  ! [Telegram Failed] {job['title']}")
            else:
                # Mark as seen locally
                mark_job_sent(url, job["title"], job["company"], job["location"], job["source"])
                print(f"  + [New Job] {job['title']} @ {job['company']} ({job['location']})")
                sent_count += 1
        else:
            # Already alerted previously
            pass

    # Step 4: Save to local Markdown Report
    if new_jobs:
        save_to_markdown_report(new_jobs)
    else:
        print("[Status] No new unseen jobs found in this run (all matches already tracked).")

    # Step 5: Send Telegram summary
    if telegram_enabled and sent_count > 0:
        send_daily_summary(total_found=len(jobs), total_sent=sent_count)

    print(f"\n[Done] Processed {len(jobs)} active listings. Sent/logged {sent_count} new openings.")
    print(f"[Database] Total lifetime tracked jobs: {get_stats()}")

if __name__ == "__main__":
    main()
