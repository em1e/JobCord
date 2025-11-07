import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_academicwork(query="developer"):
    url = f"https://www.academicwork.fi/avoimet-tyopaikat?query={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job in soup.select("li.sc-bZkfAO"):
        title = job.select_one("h3")
        company = job.select_one("span.sc-gswNZR")
        link = job.select_one("a")
        if title and company and link:
            jobs.append({
                "source": "Academic Work",
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": "Finland",
                "link": "https://www.academicwork.fi" + link["href"],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    return jobs