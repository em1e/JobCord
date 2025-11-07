import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

CUSTOM_DB = "data/custom_sources.db"

def get_custom_sources(discord_id=None):
    conn = sqlite3.connect(CUSTOM_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS custom_sources(
            discord_id TEXT,
            url TEXT,
            PRIMARY KEY(discord_id, url)
        )
    ''')
    if discord_id:
        c.execute("SELECT url FROM custom_sources WHERE discord_id=?", (discord_id,))
    else:
        c.execute("SELECT url FROM custom_sources")
    urls = [row[0] for row in c.fetchall()]
    conn.close()
    return urls

def add_custom_source(discord_id, url):
    conn = sqlite3.connect(CUSTOM_DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO custom_sources(discord_id, url) VALUES(?, ?)", (discord_id, url))
    conn.commit()
    conn.close()

def scrape_custom_urls(discord_id=None):
    jobs = []
    for url in get_custom_sources(discord_id):
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            for job in soup.select("a.job-link"):
                jobs.append({
                    "source": url,
                    "title": job.get_text(strip=True),
                    "company": "Custom",
                    "location": "Unknown",
                    "link": job['href'],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        except Exception as e:
            print(f"Failed scraping {url}: {e}")
    return jobs