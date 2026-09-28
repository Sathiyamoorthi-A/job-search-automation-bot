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
    EXCLUDE_TITLE_PATTERNS,
    STAFFING_AGENCY_KEYWORDS,
    DIRECT_ATS_DOMAINS
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_staffing_agency(company_name: str) -> bool:
    """Detects and excludes third-party staffing agencies, recruitment consultancies, and ghost reposters."""
    c_lower = company_name.lower()
    for kw in STAFFING_AGENCY_KEYWORDS:
        if kw in c_lower:
            return True
    return False

def is_direct_ats_domain(url: str) -> bool:
    """Checks whether the posting URL is hosted directly on an Enterprise ATS or Company Career domain."""
    u_lower = url.lower()
    for domain in DIRECT_ATS_DOMAINS:
        if domain in u_lower:
            return True
    return False

def extract_hr_email(text: str) -> str:
    """Extracts direct HR hiring emails if present in the posting snippet."""
    if not text:
        return ""
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if emails:
        for email in emails:
            # Avoid generic no-reply or system emails
            if not any(x in email.lower() for x in ["noreply", "no-reply", "donotreply", "support@", "info@"]):
                return email
    return ""

def is_relevant_job(title: str, company: str = "") -> bool:
    """Verifies that the job title strictly matches 0-4 YOE Associate Java developer profile and is not a staffing agency."""
    if company and is_staffing_agency(company):
        return False
        
    t_lower = title.lower()
    
    # 1. Regex check for senior / 5+ years / irrelevant roles
    for pattern in EXCLUDE_TITLE_PATTERNS:
        if re.search(pattern, t_lower):
            return False
            
    # 2. Check primary tech inclusion (Java / Spring / React / Full Stack)
    for incl in PRIMARY_MATCH_KEYWORDS:
        if incl in t_lower:
            return True
            
    return False

def clean_url(url: str) -> str:
    """Strips tracking queries from URL."""
    if not url:
        return ""
    return url.split("?")[0].strip()

def scrape_linkedin_direct_company_jobs(max_pages_per_query: int = 2) -> list:
    """Scrapes LinkedIn guest search for direct corporate hiring posts (filtering out staffing agencies)."""
    all_jobs = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        for location in TARGET_LOCATIONS:
            for page in range(max_pages_per_query):
                start = page * 25
                encoded_query = urllib.parse.quote(query)
                encoded_loc = urllib.parse.quote(location)
                encoded_exp = urllib.parse.quote(LINKEDIN_EXP_FILTER)
                
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
                            raw_company = company_el.text.strip() if company_el else "Direct Corporate Hiring"
                            raw_link = clean_url(link_el.get("href", ""))
                            
                            if not raw_link or raw_link in seen_urls:
                                continue
                                
                            if not is_relevant_job(raw_title, raw_company):
                                continue
                            
                            seen_urls.add(raw_link)
                            
                            # Check HR email in card snippet if available
                            card_text = card.text
                            found_email = extract_hr_email(card_text)
                            
                            job_data = {
                                "title": raw_title,
                                "company": raw_company,
                                "location": loc_el.text.strip() if loc_el else location,
                                "url": raw_link,
                                "source": "Direct Corporate Career Portal",
                                "time_posted": time_el.text.strip() if time_el else "Recently",
                                "hr_email": found_email,
                                "is_direct_ats": is_direct_ats_domain(raw_link)
                            }
                            all_jobs.append(job_data)
                            
                    time.sleep(0.8)
                except Exception:
                    break

    return all_jobs

def scrape_remotive_direct_jobs() -> list:
    """Fetches remote software developer jobs from direct engineering teams."""
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=30"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                company = item.get("company_name", "Direct Product Company")
                tags = [t.lower() for t in item.get("tags", [])]
                description = item.get("description", "")
                
                if is_relevant_job(title, company) and (any(t in ["java", "spring", "react", "fullstack"] for t in tags) or "java" in title.lower()):
                    job_url = clean_url(item.get("url", ""))
                    found_email = extract_hr_email(description)
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": item.get("candidate_required_location", "Worldwide Remote"),
                        "url": job_url,
                        "source": "Direct Product Company",
                        "time_posted": item.get("publication_date", "")[:10] or "Recent",
                        "hr_email": found_email,
                        "is_direct_ats": True
                    })
    except Exception:
        pass
    return jobs

def fetch_all_matching_jobs() -> list:
    """Aggregates direct corporate career postings (excluding staffing agencies and ghost listings)."""
    print("[Job Radar] Scanning Direct Corporate Career Portals & Direct ATS feeds...")
    linkedin_jobs = scrape_linkedin_direct_company_jobs(max_pages_per_query=2)
    remote_jobs = scrape_remotive_direct_jobs()
    combined = linkedin_jobs + remote_jobs
    return combined
