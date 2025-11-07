#!/usr/bin/env python3
"""Diagnose scraper failures by printing response info and parser results.

Run this locally to see which scrapers return HTML, status codes, and how many
jobs each scraper extracts. It prints a small snippet of the fetched HTML so
you can check if the page returned a block/redirect/login page instead of listings.
"""
import sys
import pathlib
import textwrap
import requests

# Ensure the repository root is on sys.path so `from scraper import ...` works
# even when scripts are executed from other directories or virtualenvs.
repo_root = pathlib.Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    from scraper import (
        remoteok_scraper,
        indeed_scraper,
        weworkremotely_scraper,
        linkedin_scraper,
        duunitori_scraper,
        academicwork_scraper,
    )
except Exception as e:
    print("Failed to import scraper package. Ensure you're running this script from the repository root or that the package exists.")
    print(f"Import error: {e}")
    raise


def probe(scraper_func, url=None, *args, **kwargs):
    name = scraper_func.__name__
    print(f"=== {name} ===")
    # If the scraper defines a url inside, we can't easily get it; call and catch
    try:
        # If scraper uses requests internally we can't capture the response without
        # modifying its code; as a workaround, try to call it and capture returned jobs
        jobs = scraper_func(*args, **kwargs)
        print(f"Parsed jobs: {len(jobs)}")
        if jobs:
            print("First job:")
            print(jobs[0])
        else:
            print("No jobs parsed. Trying a direct fetch of the target URL (if provided) to inspect HTML snippet...")
            if url:
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                print(f"Status: {r.status_code}, Content length: {len(r.text)}")
                print(textwrap.indent(r.text[:1000], "    "))
            else:
                print("No URL provided to fetch. Consider running individual scrapers manually or passing a url.")
    except Exception as e:
        print(f"Scraper raised exception: {e}")


def main():
    probe(remoteok_scraper.scrape_remoteok, url="https://remoteok.com/remote-developer-jobs")
    probe(indeed_scraper.scrape_indeed, url="https://www.indeed.com/jobs?q=developer&l=helsinki")
    probe(weworkremotely_scraper.scrape_weworkremotely, url="https://weworkremotely.com/categories/remote-programming-jobs")
    probe(linkedin_scraper.scrape_linkedin, url="https://www.linkedin.com/jobs/search/?keywords=developer&location=remote")
    probe(duunitori_scraper.scrape_duunitori, url="https://duunitori.fi/tyopaikat/haku/developer/")
    probe(academicwork_scraper.scrape_academicwork, url="https://www.academicwork.fi/avoimet-tyopaikat?query=developer")


if __name__ == '__main__':
    main()
