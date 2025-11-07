import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_weworkremotely():
    url = "https://weworkremotely.com/categories/remote-programming-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

    jobs = []
    for section in soup.select("section.jobs"):
        for job in section.select("li a[href*='/remote-jobs/']"):
            title = job.select_one("span.title")
            company = job.select_one("span.company")
            if title and company:
                jobs.append({
                    "source": "WeWorkRemotely",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "Remote",
                    "link": "https://weworkremotely.com" + job["href"],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    return jobs