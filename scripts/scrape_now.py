#!/usr/bin/env python3
"""Run the project's scrapers and print a short report.

Usage:
  python scripts/scrape_now.py

This will call `scraper.scrape_manager.scrape_all()` which populates
`src/data/developer_jobs.csv`. Any exceptions from individual scrapers
will be printed to stdout.
"""
import sys
import traceback

from scraper.scrape_manager import scrape_all


def main():
    try:
        df = scrape_all()
        print(f"Scraped {len(df)} jobs and wrote to src/data/developer_jobs.csv")
        try:
            print(df.head().to_string(index=False))
        except Exception:
            # pandas may not be present in minimal environments
            print("(Unable to pretty-print dataframe; pandas may be missing)")
    except Exception:
        print("Scrape failed with exception:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
