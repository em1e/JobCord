import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_weworkremotely():
    url = "https://weworkremotely.com/categories/remote-programming-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)

    jobs = []

    # If site returns an RSS/XML feed, parse it as XML and extract <item> entries.
    text = r.text.lstrip()
    if text.startswith("<?xml") or "<rss" in text[:200]:
        soup = BeautifulSoup(text, "xml")
        for item in soup.find_all('item'):
            title_tag = item.find('title')
            link_tag = item.find('link') or item.find('guid')
            region_tag = item.find('region')
            company = None
            # some feeds embed html in description with company info
            description = item.find('description')
            if description and '<' in description.text:
                # extract plain text fallback
                desc_soup = BeautifulSoup(description.text, 'html.parser')
                # try to find company in description text heuristically
                company = desc_soup.get_text().split('\n')[0].strip()[:100]

            jobs.append({
                "source": "WeWorkRemotely",
                "title": title_tag.text.strip() if title_tag else "",
                "company": company or "Unknown",
                "location": region_tag.text.strip() if region_tag else "Remote",
                "link": link_tag.text.strip() if link_tag and link_tag.text else None,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        return jobs

    # Fallback: parse as HTML (old behavior)
    soup = BeautifulSoup(text, "html.parser")
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