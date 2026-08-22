import os
import re
from dotenv import load_dotenv

# Explicitly load .env from the script directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# Telegram Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Candidate Profile Search Matrix
CANDIDATE_NAME = "Sathiyamoorthi Angappan"

SEARCH_QUERIES = [
    "Java Developer",
    "Java Spring Boot Developer",
    "Java Full Stack Developer",
    "Associate Software Engineer Java",
    "Junior Java Developer",
    "Java Backend Developer",
    "React Java Developer"
]

TARGET_LOCATIONS = [
    "India",
    "Bengaluru, Karnataka, India",
    "Chennai, Tamil Nadu, India",
    "Coimbatore, Tamil Nadu, India",
    "Hyderabad, Telangana, India"
]

# Time range for listings: 'r86400' = past 24 hours (daily alerts), 'r604800' = past week
TIME_FILTER = "r86400"

# LinkedIn Experience Filter: 2 = Entry Level (0-2 yrs), 3 = Associate (1-4 yrs)
# Eliminates Mid-Senior (4), Director (5), Executive (6)
LINKEDIN_EXP_FILTER = "2,3"

# Must include at least one of these primary skills/roles
PRIMARY_MATCH_KEYWORDS = [
    "java", "spring", "springboot", "full stack", "fullstack", "react", "backend developer", "software engineer", "developer"
]

# Strict exclusions for Seniority & 5+ Years Experience
EXCLUDE_TITLE_PATTERNS = [
    # Seniority & Leadership Titles
    r"\bsenior\b", r"\bsr\.?\b", r"\blead\b", r"\bprincipal\b", r"\barchitect\b",
    r"\bmanager\b", r"\bdirector\b", r"\bstaff\b", r"\bvp\b", r"\bavp\b",
    r"\bvice president\b", r"\bhead\b", r"\btech lead\b", r"\bteam lead\b",
    r"\bsde\s*(?:iii|iv|3|4)\b", r"\bsoftware engineer\s*(?:iii|iv|3|4)\b",
    r"\bdeveloper\s*(?:iii|iv|3|4|iv)\b", r"\bexpert\b",

    # Explicit 5+ / 6+ / 7+ / 8+ / 10+ Years markers
    r"\b[5-9]\+?\s*(?:years?|yrs?|yoe)\b",
    r"\b1[0-9]\+?\s*(?:years?|yrs?|yoe)\b",
    r"\b(?:5|6|7|8|9|10)\s*-\s*(?:8|9|10|12|15)\s*(?:years?|yrs?|yoe)\b",

    # Unrelated tech stacks / roles
    r"\b\.net\b", r"\bc#\b", r"\bgolang\b", r"\bphp\b", r"\bruby\b",
    r"\bios\b", r"\bandroid\b", r"\bflutter\b", r"\bdata engineer\b",
    r"\bmachine learning\b", r"\bml engineer\b", r"\baiml\b",
    r"\bsalesforce\b", r"\bdynamics\b", r"\bsap\b", r"\bdesktop support\b",
    r"\bhelp desk\b", r"\bgraphic designer\b", r"\bmaster data\b",
    r"\bqa automation\b", r"\bsdet\b"
]
