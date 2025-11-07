from __future__ import annotations

from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from jobsky.model import JobPost, JobResponse, Scraper, ScraperInput, Site
from jobsky.util import create_session, create_logger

log = create_logger("MonsterFI")


class MonsterFI(Scraper):
    base_url = "https://www.monster.fi"
    search_url = "https://www.monster.fi/jobs/search/"
    delay = 1

    def __init__(self, proxies: list[str] | str | None = None, ca_cert: str | None = None, user_agent: str | None = None):
        super().__init__(Site.OTHER, proxies=proxies, ca_cert=ca_cert, user_agent=user_agent)
        self.session = create_session(proxies=self.proxies, ca_cert=ca_cert, has_retry=True, delay=self.delay, user_agent=user_agent)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        jobs: List[JobPost] = []
        try:
            params = {"q": scraper_input.search_term} if getattr(scraper_input, "search_term", None) else {}
            resp = self.session.get(self.search_url, params=params, timeout=getattr(scraper_input, "request_timeout", 30))
            if resp.status_code != 200:
                log.error(f"MonsterFI HTTP {resp.status_code}")
                return JobResponse(jobs=[])

            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/job/" in href or "/jobs/" in href:
                    url = href if href.startswith("http") else urljoin(self.base_url, href)
                    title = a.get_text(strip=True) or "N/A"
                    jobs.append(JobPost(id=f"monster-{hash(url)}", title=title, job_url=url))
                    if len(jobs) >= scraper_input.results_wanted:
                        break
        except Exception as e:
            log.error(f"MonsterFI scrape error: {e}")

        return JobResponse(jobs=jobs[: scraper_input.results_wanted])
