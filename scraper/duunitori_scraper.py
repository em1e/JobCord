import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_duunitori(query="developer", location=""):
    url = f"https://duunitori.fi/tyopaikat/haku/{query}/{location}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job in soup.select("article.job-box"):
        title = job.select_one("h3 a")
        company = job.select_one("span.company")
        location_tag = job.select_one("span.job-location")
        if title and company:
            jobs.append({
                "source": "Duunitori",
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location_tag.get_text(strip=True) if location_tag else "Unknown",
                "link": "https://duunitori.fi" + title["href"],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    return jobs
