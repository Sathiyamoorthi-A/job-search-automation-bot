import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse
from config import (
    SEARCH_QUERIES,
    TARGET_LOCATIONS,
    TIME_FILTER,
    LINKEDIN_EXP_FILTER,
    PRIMARY_MATCH_KEYWORDS,
    EXCLUDE_TITLE_PATTERNS
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_relevant_job(title: str) -> bool:
    """Verifies that the job title strictly matches 0-4 YOE Associate / Mid Java developer profile."""
    t_lower = title.lower()
    
    # 1. Regex check for senior / 5+ years / irrelevant roles
    for pattern in EXCLUDE_TITLE_PATTERNS:
        if re.search(pattern, t_lower):
            return False
            
    # 2. Check primary tech inclusion (Java / Spring / React / Full Stack)
    has_primary = False
    for incl in PRIMARY_MATCH_KEYWORDS:
        if incl in t_lower:
            has_primary = True
            break
            
    return has_primary

def clean_url(url: str) -> str:
    """Strips tracking queries from URL."""
    if not url:
        return ""
    return url.split("?")[0].strip()

def scrape_linkedin_jobs(max_pages_per_query: int = 2) -> list:
    """Scrapes LinkedIn guest job search endpoint filtered specifically by Entry & Associate level."""
    all_jobs = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        for location in TARGET_LOCATIONS:
            for page in range(max_pages_per_query):
                start = page * 25
                encoded_query = urllib.parse.quote(query)
                encoded_loc = urllib.parse.quote(location)
                encoded_exp = urllib.parse.quote(LINKEDIN_EXP_FILTER)
                
                # f_E=2,3 limits results to Entry level & Associate (0-4 YOE)
                url = (
                    f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                    f"?keywords={encoded_query}&location={encoded_loc}&f_TPR={TIME_FILTER}&f_E={encoded_exp}&start={start}"
                )
                
                try:
                    res = requests.get(url, headers=HEADERS, timeout=12)
                    if res.status_code != 200:
                        break
                    
                    soup = BeautifulSoup(res.text, "html.parser")
                    job_cards = soup.find_all("li")
                    if not job_cards:
                        break
                    
                    for card in job_cards:
                        title_el = card.find("h3", class_="base-search-card__title")
                        company_el = card.find("h4", class_="base-search-card__subtitle")
                        loc_el = card.find("span", class_="job-search-card__location")
                        link_el = card.find("a", class_="base-card__full-link")
                        time_el = card.find("time", class_="job-search-card__listdate") or card.find("time", class_="job-search-card__listdate--new")
                        
                        if title_el and link_el:
                            raw_title = title_el.text.strip()
                            raw_link = clean_url(link_el.get("href", ""))
                            
                            if not raw_link or raw_link in seen_urls:
                                continue
                                
                            if not is_relevant_job(raw_title):
                                continue
                            
                            seen_urls.add(raw_link)
                            
                            job_data = {
                                "title": raw_title,
                                "company": company_el.text.strip() if company_el else "Confidential",
                                "location": loc_el.text.strip() if loc_el else location,
                                "url": raw_link,
                                "source": "LinkedIn",
                                "time_posted": time_el.text.strip() if time_el else "Recently"
                            }
                            all_jobs.append(job_data)
                            
                    time.sleep(0.8)
                except Exception:
                    break

    return all_jobs

def scrape_remotive_jobs() -> list:
    """Fetches remote software developer jobs filtered for non-senior Java / React roles."""
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=30"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                tags = [t.lower() for t in item.get("tags", [])]
                
                if is_relevant_job(title) and (any(t in ["java", "spring", "react", "fullstack"] for t in tags) or "java" in title.lower()):
                    jobs.append({
                        "title": title,
                        "company": item.get("company_name", "Remote Company"),
                        "location": item.get("candidate_required_location", "Worldwide Remote"),
                        "url": clean_url(item.get("url", "")),
                        "source": "Remotive Remote",
                        "time_posted": item.get("publication_date", "")[:10] or "Recent"
                    })
    except Exception:
        pass
    return jobs

def fetch_all_matching_jobs() -> list:
    """Aggregates all matching jobs strictly filtered for 0-4 YOE."""
    print("[Job Radar] Scanning jobs with strict 0-4 YOE filters (Entry & Associate level)...")
    linkedin_jobs = scrape_linkedin_jobs(max_pages_per_query=2)
    remote_jobs = scrape_remotive_jobs()
    combined = linkedin_jobs + remote_jobs
    return combined
