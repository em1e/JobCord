from __future__ import annotations

from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from jobsky.model import JobPost, JobResponse, Scraper, ScraperInput, Site
from jobsky.util import create_session, create_logger

log = create_logger("AcademicWork")


class AcademicWork(Scraper):
    base_url = "https://www.academicwork.fi"
    search_url = "https://www.academicwork.fi/tyopaikat"
    delay = 1

    def __init__(self, proxies: list[str] | str | None = None, ca_cert: str | None = None, user_agent: str | None = None):
        super().__init__(Site.OTHER, proxies=proxies, ca_cert=ca_cert, user_agent=user_agent)
        self.session = create_session(proxies=self.proxies, ca_cert=ca_cert, has_retry=True, delay=self.delay, user_agent=user_agent)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        jobs: List[JobPost] = []
        try:
            params = {"q": scraper_input.search_term} if getattr(scraper_input, "search_term", None) else {}
            resp = self.session.get(self.search_url, params=params, timeout=getattr(scraper_input, "request_timeout", 30), allow_redirects=True)
            if resp.status_code >= 400:
                log.error(f"AcademicWork HTTP {resp.status_code}")
                return JobResponse(jobs=[])

            final_base = resp.url if getattr(resp, "url", None) else self.base_url
            soup = BeautifulSoup(resp.text or "", "html.parser")

            anchors = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(fragment in href for fragment in ("/jobs/", "/tyopaikat/", "/vacancy/")):
                    anchors.append(a)

            # If we couldn't find anchors, search for job-listing blocks and then their anchors
            if not anchors:
                cards = soup.find_all(class_=lambda v: v and any(k in v.lower() for k in ("job", "position", "vacancy")))
                for card in cards:
                    a = card.find("a", href=True)
                    if a:
                        anchors.append(a)

            for a in anchors:
                href = a.get("href")
                if not href:
                    continue
                url = href if href.startswith("http") else urljoin(final_base, href)
                title = a.get_text(strip=True) or a.get("aria-label") or a.get("title") or "N/A"
                try:
                    jobs.append(JobPost(id=f"academicwork-{abs(hash(url))}", title=title, job_url=url))
                except Exception:
                    jobs.append(JobPost(id=f"academicwork-{abs(hash(url))}", title=title, job_url=url))
                if len(jobs) >= scraper_input.results_wanted:
                    break
        except Exception as e:
            log.error(f"AcademicWork scrape error: {e}")

        return JobResponse(jobs=jobs[: scraper_input.results_wanted])
