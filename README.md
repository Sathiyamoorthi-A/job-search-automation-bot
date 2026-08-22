# 🎯 Automated Daily Job Search & Telegram Alert Radar

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-0088cc.svg)](https://core.telegram.org/bots/api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated, zero-cost, multi-platform **Job Search & Alert Radar** built in Python. It scrapes newly posted tech roles from platforms like **LinkedIn** and **Remote Boards**, filters them strictly by tech stack, target locations, and experience level (e.g., **0–4 YOE Entry/Associate**), prevents duplicate alerts using SQLite, and delivers instant HTML notification cards directly to your **Telegram** phone app.

---

## ✨ Features

- ⚡ **Real-Time Job Scraping:** Scrapes active postings published within the last 24 hours.
- 🎯 **Dual-Layer Experience Filtering:** Uses API parameters (`f_E=2,3`) plus Regex exclusion rules to eliminate 5+ YOE, Senior, Lead, Principal, and Architect roles.
- 📱 **Instant Telegram Push Notifications:** Sends clean HTML job cards with direct **1-Click Apply Links**, company names, and locations.
- 🗄️ **SQLite Deduplication Engine:** Stores alerted job URLs in `jobs_history.db` so you never get the same alert twice.
- 📄 **Local Markdown Summary Reports:** Automatically generates `latest_jobs_report.md` for quick offline browsing.
- ⏰ **Set-and-Forget Daily Automation:** Compatible with **Windows Task Scheduler**, **macOS/Linux Cron**, or **GitHub Actions**.

---

## 🛠️ How to Setup for Your Own Job Search Requirements

Follow this guide to customize and deploy this tool for your own tech stack and profile (e.g., *Java, Python, Full Stack, Data Science, Frontend, DevOps, etc.*).

### 1. Prerequisites
- **Python 3.9+** installed on your system.
- A **Telegram Account** on your mobile phone or desktop.

---

### 2. Clone Repository & Install Dependencies

```bash
git clone https://github.com/Sathiyamoorthi-A/job-search-automation-bot.git
cd job-search-automation-bot
pip install -r requirements.txt
```

---

### 3. Create & Configure Telegram Bot (2 Minutes)

1. Open Telegram and search for **`@BotFather`**.
2. Send `/newbot`, choose a Bot Name and Username (e.g., `my_job_radar_bot`).
3. Copy the **HTTP API Token** provided by `@BotFather`.
4. Open Telegram and search for **`@userinfobot`** (or `@getmyid_bot`), click **Start**, and copy your numerical **Chat ID**.
5. Click **Start** on your newly created bot chat so it has permission to message you.

Create a `.env` file in the project root directory (or copy `.env.example`):
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

### 4. Customize for Your Profile (`config.py`)

Open `config.py` and customize the variables for your target domain:

#### A. Target Search Queries & Locations
```python
SEARCH_QUERIES = [
    "Java Spring Boot Developer",
    "Java Full Stack Developer",
    "Associate Software Engineer Java",
    "Junior Java Developer"
]

TARGET_LOCATIONS = [
    "India",
    "Bengaluru, Karnataka, India",
    "Chennai, Tamil Nadu, India",
    "Remote"
]
```

#### B. Experience Level Filter
- `LINKEDIN_EXP_FILTER = "2,3"`: Restricts LinkedIn search to **Entry Level (0–2 YOE)** and **Associate Level (1–4 YOE)**.
- For Mid-Senior roles (5+ yrs), set `LINKEDIN_EXP_FILTER = "4"`.

#### C. Positive & Exclusion Keywords
```python
# Keywords that MUST be present in the job title
PRIMARY_MATCH_KEYWORDS = ["java", "spring", "full stack", "backend", "software engineer"]

# Title patterns to REJECT automatically
EXCLUDE_TITLE_PATTERNS = [
    r"\bsenior\b", r"\bsr\.?\b", r"\blead\b", r"\bprincipal\b", r"\barchitect\b",
    r"\bmanager\b", r"\bdirector\b", r"\b5\+?\s*(?:years?|yrs?)\b"
]
```

---

### 5. Run & Test

#### Test Telegram Connection:
```bash
python main.py --test
```
*(You will receive a confirmation message in your Telegram app).*

#### Run Live Job Radar Scan:
```bash
python main.py
```

---

### 6. Schedule Automated Daily Execution

#### Windows (Task Scheduler):
1. Press `Win + S`, search for **Task Scheduler**, and open it.
2. Click **Create Basic Task** -> Name: `Daily Job Radar`.
3. Trigger: **Daily** at `09:00 AM`.
4. Action: **Start a program**.
5. Program: `C:\Users\YourUsername\job-search-automation-bot\run_daily_job_alerts.bat` (or select `python.exe` with arguments `main.py`).
6. Start in: `C:\Users\YourUsername\job-search-automation-bot`

#### Linux / macOS (Cron):
Open crontab:
```bash
crontab -e
```
Add daily schedule at 9:00 AM:
```cron
0 9 * * * cd /path/to/job-search-automation-bot && /usr/bin/python3 main.py >> job_bot.log 2>&1
```

---

## 📂 Project Architecture

```text
├── config.py              # User search matrix, experience filters, & keywords
├── scrapers.py            # Multi-provider web scrapers (LinkedIn, Remotive)
├── storage.py             # SQLite deduplication storage engine (jobs_history.db)
├── telegram_notifier.py   # Telegram Bot API message formatting & delivery
├── main.py                # Main pipeline orchestrator & CLI runner
├── requirements.txt       # Project dependencies
├── .env.example           # Environment template for credentials
├── .gitignore             # Ignored runtime artifacts & environment files
└── README.md              # Project documentation
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

**Sathiyamoorthi Angappan**  
- **LinkedIn:** [sathiyamoorthi-a94957717b](https://www.linkedin.com/in/sathiyamoorthi-a94957717b)  
- **GitHub:** [Sathiyamoorthi-A](https://github.com/Sathiyamoorthi-A)
