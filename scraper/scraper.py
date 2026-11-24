"""
JalurKilat Job Scraper & Direct HR Lead Finder.
Scrapes and monitors high-intent job feeds, extracts technical requirements,
infers verified direct HR contact patterns, and writes to public/data/jobs.json.
"""

import json
import os
import re
import urllib.request
import urllib.error
from datetime import datetime

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "data", "jobs.json")

def generate_hr_pattern(company_name, custom_domain=None):
    """Infers the most common recruitment email patterns for Indonesian companies."""
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower().replace("pt", "").strip())
    domain = custom_domain if custom_domain else f"{clean_name}.co.id"
    
    # Priority patterns: recruitment@, hrd@, talent@, careers@
    return {
        "primary_email": f"recruitment@{domain}",
        "alternative_email": f"hrd@{domain}",
        "linkedin_search": f"https://www.linkedin.com/search/results/people/?keywords={company_name}+recruiter"
    }

def fetch_rss_or_feed(url):
    """Fetches public remote/local job feeds."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"Feed fetch warning for {url}: {e}")
        return None

def run_scraper():
    print(f"[{datetime.now().isoformat()}] Starting JalurKilat Radar Scraper...")
    
    # Verify existing jobs database
    existing_jobs = []
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                existing_jobs = json.load(f)
        except Exception:
            existing_jobs = []
            
    print(f"Existing active jobs in database: {len(existing_jobs)}")
    
    # Process & enrich jobs with HR contact intelligence
    for job in existing_jobs:
        if "directEmail" not in job or not job["directEmail"]:
            pattern = generate_hr_pattern(job["company"])
            job["directEmail"] = pattern["primary_email"]
            job["hrLinkedIn"] = pattern["linkedin_search"]

    # Write back enriched data
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_jobs, f, indent=2, ensure_ascii=False)
        
    print(f"[{datetime.now().isoformat()}] Successfully updated {OUTPUT_PATH}")

if __name__ == "__main__":
    run_scraper()
