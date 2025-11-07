import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_indeed(query="developer", location="helsinki"):
    url = f"https://www.indeed.com/jobs?q={query}&l={location}"
    headers = {"User-Agent": "Mozilla/5.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

    jobs = []
    for card in soup.select("div.job_seen_beacon"):
        title = card.select_one("h2 span")
        company = card.select_one("span.companyName")
        location = card.select_one("div.companyLocation")
        link_tag = card.select_one("a")

        if title and company:
            jobs.append({
                "source": "Indeed",
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location.text.strip() if location else "Remote",
                "link": "https://www.indeed.com" + link_tag["href"] if link_tag else None,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    return jobs