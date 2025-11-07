import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

def scrape_linkedin(query="developer", location="remote"):
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(query)}&location={urllib.parse.quote(location)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job in soup.select("li.base-card"):
        title = job.select_one("h3.base-search-card__title")
        company = job.select_one("h4.base-search-card__subtitle")
        link = job.select_one("a.base-card__full-link")
        location = job.select_one("span.job-search-card__location")
        if title and company:
            jobs.append({
                "source": "LinkedIn",
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location.get_text(strip=True) if location else "Unknown",
                "link": link["href"] if link else None,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
    return jobs