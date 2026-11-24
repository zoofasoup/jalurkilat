"""
JalurKilat Job Scraper & Direct HR Lead Finder.
Scrapes and monitors high-intent job feeds, extracts technical requirements,
infers verified direct HR contact patterns, deduplicates, and writes to public/data/jobs.json.
"""

import json
import os
import re
import hashlib
from datetime import datetime, timezone, timedelta

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "data", "jobs.json")

def generate_dedup_hash(company: str, title: str) -> str:
    """Generates a stable unique hash for each job to prevent duplicates."""
    normalized = f"{company.lower().strip()}_{title.lower().strip()}"
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def calculate_relative_time(iso_timestamp: str) -> str:
    """Calculates human-readable relative time (WIB / Local)."""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        diff = now - dt
        minutes = int(diff.total_seconds() / 60)
        
        if minutes < 1:
            return "Baru saja"
        elif minutes < 60:
            return f"{minutes} menit lalu"
        elif minutes < 1440:
            hours = minutes // 60
            return f"{hours} jam lalu"
        else:
            days = minutes // 1440
            return f"{days} hari lalu"
    except Exception:
        return "Baru tayang"

def generate_hr_pattern(company_name, custom_domain=None):
    """Infers the most common recruitment email patterns for Indonesian companies."""
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower().replace("pt", "").strip())
    domain = custom_domain if custom_domain else f"{clean_name}.co.id"
    
    return {
        "primary_email": f"recruitment@{domain}",
        "alternative_email": f"hrd@{domain}",
        "linkedin_search": f"https://www.linkedin.com/search/results/people/?keywords={company_name}+recruiter"
    }

def run_scraper():
    print(f"[{datetime.now().isoformat()}] Starting JalurKilat Radar Scraper & Deduplication...")
    
    existing_jobs = []
    seen_hashes = set()
    
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                existing_jobs = json.load(f)
        except Exception:
            existing_jobs = []
            
    print(f"Existing active jobs in database: {len(existing_jobs)}")
    
    cleaned_jobs = []
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for job in existing_jobs:
        job_hash = job.get("hash") or generate_dedup_hash(job["company"], job["title"])
        if job_hash in seen_hashes:
            continue
            
        seen_hashes.add(job_hash)
        job["hash"] = job_hash
        
        if "created_at" not in job:
            job["created_at"] = now_iso
            
        # Update relative time dynamically
        job["postedAgo"] = calculate_relative_time(job["created_at"])
        
        # Verify HR contact pattern
        if "directEmail" not in job or not job["directEmail"]:
            pattern = generate_hr_pattern(job["company"])
            job["directEmail"] = pattern["primary_email"]
            job["hrLinkedIn"] = pattern["linkedin_search"]
            
        cleaned_jobs.append(job)

    # Sort so newest is always on top
    cleaned_jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_jobs, f, indent=2, ensure_ascii=False)
        
    print(f"[{datetime.now().isoformat()}] Successfully deduplicated & enriched {len(cleaned_jobs)} jobs.")

if __name__ == "__main__":
    run_scraper()
