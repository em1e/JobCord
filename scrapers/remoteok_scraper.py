import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_remoteok():
    url = "https://remoteok.com/remote-developer-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

    jobs = []
    for job in soup.select("tr.job"):
        title = job.select_one("h2")
        company = job.select_one(".companyLink h3")
        location = job.select_one(".location")
        link = job.get("data-href")

        if title and company:
            jobs.append({
                "source": "RemoteOK",
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location.get_text(strip=True) if location else "Remote",
                "link": f"https://remoteok.com{link}" if link else None,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    return jobs