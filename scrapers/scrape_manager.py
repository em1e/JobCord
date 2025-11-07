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
    all_jobs.extend(scrape_remoteok())
    all_jobs.extend(scrape_indeed())
    all_jobs.extend(scrape_weworkremotely())
    all_jobs.extend(scrape_linkedin())
    all_jobs.extend(scrape_duunitori())
    all_jobs.extend(scrape_academicwork())

    df = pd.DataFrame(all_jobs)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    if os.path.exists(DATA_PATH):
        old = pd.read_csv(DATA_PATH)
        last_id = old["id"].max() if "id" in old.columns else 0
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