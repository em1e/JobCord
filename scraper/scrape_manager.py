import pandas as pd
import os

from scraper.remoteok_scraper import scrape_remoteok
from scraper.indeed_scraper import scrape_indeed
from scraper.weworkremotely_scraper import scrape_weworkremotely
from scraper.linkedin_scraper import scrape_linkedin
from scraper.duunitori_scraper import scrape_duunitori
from scraper.academicwork_scraper import scrape_academicwork

DATA_PATH = "src/data/developer_jobs.csv"
OLD_PATH = "src/data/previous_jobs.csv"

def scrape_all():
    all_jobs = []
    print("🕸️ Scraping from multiple sources...")

    # helper to run a scraper and capture exceptions so one failing scraper
    # doesn't stop the whole run. It also prints a short status for each.
    def run_scraper(func, name):
        try:
            jobs = func()
            count = len(jobs) if jobs is not None else 0
            print(f"  - {name}: {count} jobs")
            return jobs or []
        except Exception as e:
            print(f"  - {name}: failed ({e})")
            return []

    all_jobs.extend(run_scraper(scrape_remoteok, "RemoteOK"))
    all_jobs.extend(run_scraper(scrape_indeed, "Indeed"))
    all_jobs.extend(run_scraper(scrape_weworkremotely, "WeWorkRemotely"))
    all_jobs.extend(run_scraper(scrape_linkedin, "LinkedIn"))
    all_jobs.extend(run_scraper(scrape_duunitori, "Duunitori"))
    all_jobs.extend(run_scraper(scrape_academicwork, "AcademicWork"))

    df = pd.DataFrame(all_jobs)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    if os.path.exists(DATA_PATH):
        old = pd.read_csv(DATA_PATH)
        # old["id"].max() can be NaN (float) if the CSV exists but has no rows.
        # Coerce to int safely and treat NaN as 0 to avoid TypeError when building range().
        if "id" in old.columns:
            max_id = old["id"].max()
            last_id = int(max_id) if pd.notna(max_id) else 0
        else:
            last_id = 0
    else:
        last_id = 0
    df.insert(0, "id", range(last_id + 1, last_id + 1 + len(df)))

    df.to_csv(DATA_PATH, index=False)
    print(f"✅ Scraped total {len(df)} jobs.")
    return df

def get_new_jobs():
    if not os.path.exists(OLD_PATH):
        print("No previous data found; initializing job list.")
        scrape_all().to_csv(OLD_PATH, index=False)
        return pd.read_csv(DATA_PATH)

    old = pd.read_csv(OLD_PATH)
    new = pd.read_csv(DATA_PATH)
    merged = new.merge(old, on=["title", "company"], how="left", indicator=True)
    new_jobs = merged[merged["_merge"] == "left_only"][["source", "title", "company", "location", "link", "date"]]
    new.to_csv(OLD_PATH, index=False)
    return new_jobs

def filter_jobs(keyword):
    if not os.path.exists(DATA_PATH):
        scrape_all()
    df = pd.read_csv(DATA_PATH)
    filtered = df[df.apply(lambda row: keyword.lower() in str(row["title"]).lower() or keyword.lower() in str(row["company"]).lower(), axis=1)]
    return filtered


def get_job_by_id(job_id: int):
    """Return a job row as a dict given its integer id from DATA_PATH.

    Returns None if not found.
    """
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH)
    if 'id' not in df.columns:
        return None
    matches = df[df['id'] == int(job_id)]
    if matches.empty:
        return None
    row = matches.iloc[0]
    return row.to_dict()