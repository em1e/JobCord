from __future__ import annotations

from typing import Optional, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from jobsky.model import JobPost, JobResponse, Scraper, ScraperInput, Site
from jobsky.util import create_session, create_logger

log = create_logger("Duunitori")


class Duunitori(Scraper):
    base_url = "https://www.duunitori.fi"
    search_url = "https://www.duunitori.fi/tyopaikat"
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
                log.error(f"Duunitori HTTP {resp.status_code}")
                return JobResponse(jobs=[])

            # Use the final URL after redirects as the base for relative links
            final_base = resp.url if getattr(resp, "url", None) else self.base_url
            soup = BeautifulSoup(resp.text or "", "html.parser")

            # Look for common job card anchors first
            anchors = []
            # heuristic 1: anchors with hrefs containing job path fragments
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(fragment in href for fragment in ("/tyopaikat/", "/job/", "/vacancy/", "/jobs/")):
                    anchors.append(a)

            # heuristic 2: if none found, look for elements that look like job cards
            if not anchors:
                possible_cards = soup.find_all(class_=lambda v: v and "job" in v.lower())
                for card in possible_cards:
                    a = card.find("a", href=True)
                    if a:
                        anchors.append(a)

            for a in anchors:
                href = a.get("href")
                if not href:
                    continue
                url = href if href.startswith("http") else urljoin(final_base, href)
                title = a.get_text(strip=True) or a.get("title") or "N/A"
                try:
                    jobs.append(JobPost(id=f"duunitori-{abs(hash(url))}", title=title, job_url=url))
                except Exception:
                    # fallback to minimal dict to avoid pydantic failures
                    jobs.append(JobPost(id=f"duunitori-{abs(hash(url))}", title=title, job_url=url))
                if len(jobs) >= scraper_input.results_wanted:
                    break
        except Exception as e:
            log.error(f"Duunitori scrape error: {e}")

        return JobResponse(jobs=jobs[: scraper_input.results_wanted])
