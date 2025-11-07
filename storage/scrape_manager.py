import pandas as pd
import os

DATA_PATH = "src/data/developer_jobs.csv"
OLD_PATH = "src/data/previous_jobs.csv"


def scrape_all():
    # Discover and run all Scraper subclasses found under the `jobsky` package.
    # This will import each submodule under `jobsky`, instantiate any class
    # that subclasses `jobsky.model.Scraper`, and call its `.scrape()` method
    # with a minimal `ScraperInput` requesting `results_wanted` jobs.
    all_jobs = []

    try:
        import importlib
        import inspect
        import pkgutil

        import jobsky
        from jobsky.model import ScraperInput, Scraper

        print("🕸️ Discovering scrapers in the jobsky package...")

        seen_classes = set()
        # Iterate submodules in jobsky and import them
        for finder, mod_name, ispkg in pkgutil.iter_modules(jobsky.__path__):
            try:
                module = importlib.import_module(f"jobsky.{mod_name}")
            except Exception as e:
                print(f"  - failed to import jobsky.{mod_name}: {e}")
                continue

            # Find Scraper subclasses in the module
            for _, obj in inspect.getmembers(module, inspect.isclass):
                try:
                    if obj is Scraper or not issubclass(obj, Scraper):
                        continue
                except Exception:
                    continue

                # Avoid duplicate scraper classes
                if obj in seen_classes:
                    continue
                seen_classes.add(obj)

                try:
                    scraper = obj()  # instantiate with default args
                    # Build a minimal ScraperInput that targets this scraper's site
                    # Use empty search_term instead of None to avoid constructing URLs
                    # with 'None' in scrapers that interpolate the search term.
                    scraper_input = ScraperInput(site_type=[scraper.site], results_wanted=50, search_term="")
                    print(f"  - running scraper: {obj.__name__} (site={scraper.site})")
                    resp = scraper.scrape(scraper_input)
                    jobs = getattr(resp, "jobs", []) or []

                    for job in jobs:
                        job_data = job.dict()
                        # Map to legacy dict fields
                        date_val = job_data.get("date_posted") or job_data.get("date")
                        if hasattr(date_val, "isoformat"):
                            date_val = date_val.isoformat()

                        location = None
                        if job_data.get("location"):
                            try:
                                # Some Location objects implement display_location()
                                location_obj = job_data.get("location")
                                if hasattr(location_obj, "display_location"):
                                    location = location_obj.display_location()
                                else:
                                    # could be a dict
                                    loc_parts = []
                                    if isinstance(location_obj, dict):
                                        if location_obj.get("city"):
                                            loc_parts.append(location_obj.get("city"))
                                        if location_obj.get("state"):
                                            loc_parts.append(location_obj.get("state"))
                                        if location_obj.get("country"):
                                            loc_parts.append(str(location_obj.get("country")))
                                        location = ", ".join(loc_parts) if loc_parts else None
                            except Exception:
                                location = None

                        all_jobs.append({
                            "source": scraper.site.value if getattr(scraper, "site", None) else job_data.get("site") or "",
                            "title": job_data.get("title") or job_data.get("id") or "",
                            "company": job_data.get("company_name") or job_data.get("company") or "",
                            "location": location,
                            "link": job_data.get("job_url") or job_data.get("job_url_direct") or job_data.get("company_url") or job_data.get("link"),
                            "date": date_val or "",
                        })
                except Exception as e:
                    print(f"    - scraper {obj.__name__} failed: {e}")

        print(f"  - discovered total {len(all_jobs)} jobs from jobsky scrapers")

        # Now include any watchlist URLs (company job pages or direct listings)
        try:
            from storage.watchlist import load_watchlist
            from jobsky.util import create_session

            watch_items = load_watchlist()
            if watch_items:
                print(f"  - processing {len(watch_items)} watchlist URLs")
                session = create_session(user_agent=None)
                for item in watch_items:
                    url = item.get("url") if isinstance(item, dict) else item
                    try:
                        resp = session.get(url, timeout=30)
                        if resp.status_code != 200:
                            print(f"    - watchlist URL {url} returned {resp.status_code}")
                            continue
                        from bs4 import BeautifulSoup

                        soup = BeautifulSoup(resp.text, "html.parser")
                        # Heuristic: collect prominent job links from the page
                        count = 0
                        for a in soup.find_all("a", href=True):
                            href = a["href"]
                            if any(token in href.lower() for token in ["job", "careers", "vacancy", "vacancies", "position"]):
                                link = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                                title = a.get_text(strip=True) or link
                                all_jobs.append({
                                    "source": "watchlist",
                                    "title": title,
                                    "company": item.get("note", "") if isinstance(item, dict) else "",
                                    "location": None,
                                    "link": link,
                                    "date": "",
                                })
                                count += 1
                                if count >= 10:
                                    break
                        if count == 0:
                            # If no explicit job links found, treat the page itself as a job listing
                            all_jobs.append({
                                "source": "watchlist",
                                "title": item.get("note", "watchlist") if isinstance(item, dict) else url,
                                "company": item.get("note", "") if isinstance(item, dict) else "",
                                "location": None,
                                "link": url,
                                "date": "",
                            })
                    except Exception as e:
                        print(f"    - error fetching watchlist URL {url}: {e}")
        except Exception:
            pass

    except Exception as e:
        print(f"Failed to discover/run jobsky scrapers: {e}")

    df = pd.DataFrame(all_jobs)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    # Normalize column names to align with developer_jobs.csv expected schema
    # Map our minimal fields to the richer schema used in the repo
    col_map = {
        "source": "site",
        "link": "job_url",
        "date": "date_posted",
        "title": "title",
        "company": "company",
        "location": "location",
    }
    df = df.rename(columns=col_map)

    # Full header to ensure consistent columns when appending
    HEADER = [
        "id",
        "site",
        "job_url",
        "job_url_direct",
        "title",
        "company",
        "location",
        "date_posted",
        "job_type",
        "salary_source",
        "interval",
        "min_amount",
        "max_amount",
        "currency",
        "is_remote",
        "job_level",
        "job_function",
        "listing_type",
        "emails",
        "description",
        "company_industry",
        "company_url",
        "company_logo",
        "company_url_direct",
        "company_addresses",
        "company_num_employees",
        "company_revenue",
        "company_description",
        "skills",
        "experience_range",
        "company_rating",
        "company_reviews_count",
        "vacancy_count",
        "work_from_home_type",
    ]

    # Ensure all HEADER columns exist in df; fill missing with empty values
    for col in HEADER:
        if col not in df.columns:
            df[col] = ""

    # Order columns according to HEADER (id will be added next)
    df = df[[c for c in HEADER if c != "id"]]

    # Determine last id in existing file (if any) and assign new ids sequentially
    if os.path.exists(DATA_PATH):
        try:
            existing = pd.read_csv(DATA_PATH)
            if "id" in existing.columns:
                max_id = existing["id"].max()
                last_id = int(max_id) if pd.notna(max_id) else 0
            else:
                last_id = 0
        except Exception:
            last_id = 0
    else:
        last_id = 0

    new_ids = list(range(last_id + 1, last_id + 1 + len(df)))
    df.insert(0, "id", new_ids)

    # Sanitize long text fields: user requested no long job/company descriptions
    try:
        SANITIZE_THRESHOLD = 300  # characters; anything longer will be cleared
        text_cols = df.select_dtypes(include=[object]).columns.tolist()
        for col in text_cols:
            # explicitly clear description fields
            if col in ("description", "company_description"):
                df[col] = ""
                continue
            # clear any overly long text values
            df[col] = df[col].apply(lambda v: "" if isinstance(v, str) and len(v) > SANITIZE_THRESHOLD else v)
    except Exception:
        # be conservative; if sanitization fails, continue without raising
        pass

    # Append to CSV so the file only grows row-by-row. If the file doesn't exist,
    # write the header; otherwise append without header.
    write_header = not os.path.exists(DATA_PATH)
    df.to_csv(DATA_PATH, mode="a", index=False, header=write_header)
    print(f"✅ Appended {len(df)} jobs to {DATA_PATH} (last id now {new_ids[-1] if new_ids else last_id})")
    return df

def get_new_jobs():
    if not os.path.exists(OLD_PATH):
        print("No previous data found; initializing job list.")
        scrape_all().to_csv(OLD_PATH, index=False)
        return pd.read_csv(DATA_PATH)

    old = pd.read_csv(OLD_PATH)
    new = pd.read_csv(DATA_PATH)
    merged = new.merge(old, on=["title", "company"], how="left", indicator=True)
    new_jobs = merged[merged["_merge"] == "left_only"][["source", "title", "company", "location", "link", "date"]]
    new.to_csv(OLD_PATH, index=False)
    return new_jobs

def filter_jobs(keyword):
    if not os.path.exists(DATA_PATH):
        scrape_all()
    df = pd.read_csv(DATA_PATH)
    filtered = df[df.apply(lambda row: keyword.lower() in str(row["title"]).lower() or keyword.lower() in str(row["company"]).lower(), axis=1)]
    return filtered


def get_job_by_id(job_id: int):
    """Return a job row as a dict given its integer id from DATA_PATH.

    Returns None if not found.
    """
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH)
    if 'id' not in df.columns:
        return None
    matches = df[df['id'] == int(job_id)]
    if matches.empty:
        return None
    row = matches.iloc[0]
    return row.to_dict()


def reset_job_ids(start_at: int = 1, path: str = DATA_PATH):
    """Reassign sequential integer IDs to the CSV at `path` starting from `start_at`.

    Returns the updated DataFrame, or None if the file doesn't exist or is empty.
    """
    if not os.path.exists(path):
        print(f"No file at {path} to reset IDs")
        return None

    df = pd.read_csv(path)
    if df.empty:
        print(f"File {path} is empty; nothing to reset")
        return df

    # Ensure id column exists and is integer
    df = df.copy()
    df.insert(0, "id", range(start_at, start_at + len(df)))
    df.to_csv(path, index=False)
    print(f"Reset {len(df)} ids in {path} starting at {start_at}")
    return df


def append_jobs_dataframe(df: pd.DataFrame, path: str = DATA_PATH) -> int:
    """Append a jobs DataFrame (from jobsky.scrape_jobs or similar) to the CSV at `path`.

    Returns the number of rows appended.
    """
    if df is None or df.empty:
        return 0

    # Expected canonical header used in developer_jobs.csv
    HEADER = [
        "id",
        "site",
        "job_url",
        "job_url_direct",
        "title",
        "company",
        "location",
        "date_posted",
        "job_type",
        "salary_source",
        "interval",
        "min_amount",
        "max_amount",
        "currency",
        "is_remote",
        "job_level",
        "job_function",
        "listing_type",
        "emails",
        "description",
        "company_industry",
        "company_url",
        "company_logo",
        "company_url_direct",
        "company_addresses",
        "company_num_employees",
        "company_revenue",
        "company_description",
        "skills",
        "experience_range",
        "company_rating",
        "company_reviews_count",
        "vacancy_count",
        "work_from_home_type",
    ]

    # Normalize column names from jobsky output to expected names where possible
    col_map = {
        "site": "site",
        "job_url": "job_url",
        "job_url_direct": "job_url_direct",
        "job_url_direct": "job_url_direct",
        "title": "title",
        "company_name": "company",
        "company": "company",
        "location": "location",
        "date_posted": "date_posted",
        "date": "date_posted",
    }

    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Ensure all HEADER columns exist in df; fill missing with empty values
    for col in HEADER:
        if col == "id":
            continue
        if col not in df.columns:
            df[col] = ""

    # Reorder columns (without id) to match the CSV
    df_out = df[[c for c in HEADER if c != "id"]].copy()

    # Sanitize long text fields before appending. The user requested no long
    # job descriptions, company descriptions, or anything similarly long.
    try:
        SANITIZE_THRESHOLD = 300
        # Explicitly clear the description fields
        if "description" in df_out.columns:
            df_out["description"] = ""
        if "company_description" in df_out.columns:
            df_out["company_description"] = ""

        # For any other text columns, clear values that exceed the threshold
        text_cols = df_out.select_dtypes(include=[object]).columns.tolist()
        for col in text_cols:
            df_out[col] = df_out[col].apply(lambda v: "" if isinstance(v, str) and len(v) > SANITIZE_THRESHOLD else v)
    except Exception:
        # don't fail the append if sanitization has an issue
        pass

    # Determine last id in existing file (if any) and assign new ids sequentially
    if os.path.exists(path):
        try:
            existing = pd.read_csv(path)
            if "id" in existing.columns and not existing.empty:
                max_id = existing["id"].max()
                last_id = int(max_id) if pd.notna(max_id) else 0
            else:
                last_id = 0
        except Exception:
            last_id = 0
    else:
        last_id = 0

    new_ids = list(range(last_id + 1, last_id + 1 + len(df_out)))
    df_out.insert(0, "id", new_ids)

    write_header = not os.path.exists(path)
    df_out.to_csv(path, mode="a", index=False, header=write_header)

    return len(df_out)


def scrape_watchlist(results_wanted_per_item: int = 10) -> pd.DataFrame:
    """Scrape only the URLs stored in the watchlist and return a DataFrame

    This mirrors the watchlist behavior inside `scrape_all` but focuses
    exclusively on watchlist entries so it can be used by commands that
    only want watchlist results.
    """
    try:
        from storage.watchlist import load_watchlist
        from jobsky.util import create_session
        from bs4 import BeautifulSoup
    except Exception:
        # If optional deps are missing, return empty DataFrame
        return pd.DataFrame()

    items = load_watchlist() or []
    all_jobs = []
    if not items:
        return pd.DataFrame()

    session = create_session(user_agent=None)
    for item in items:
        url = item.get("url") if isinstance(item, dict) else item
        note = item.get("note", "") if isinstance(item, dict) else ""
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text or "", "html.parser")
            count = 0
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(token in href.lower() for token in ["job", "careers", "vacancy", "vacancies", "position"]):
                    link = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                    title = a.get_text(strip=True) or link
                    all_jobs.append({
                        "site": "watchlist",
                        "job_url": link,
                        "title": title,
                        "company": note,
                        "location": None,
                        "date_posted": "",
                    })
                    count += 1
                    if count >= results_wanted_per_item:
                        break
            if count == 0:
                all_jobs.append({
                    "site": "watchlist",
                    "job_url": url,
                    "title": note or url,
                    "company": note,
                    "location": None,
                    "date_posted": "",
                })
        except Exception:
            continue

    if not all_jobs:
        return pd.DataFrame()

    df = pd.DataFrame(all_jobs)
    # Ensure canonical header and id insertion like append_jobs_dataframe expects
    # Reuse append_jobs_dataframe to normalize and append if desired; here we just
    # return the normalized DataFrame (without writing) so caller can attach or append.
    # Map minimal fields to the canonical header
    col_map = {
        "site": "site",
        "job_url": "job_url",
        "title": "title",
        "company": "company",
        "location": "location",
        "date_posted": "date_posted",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Fill missing canonical columns with empty strings (reuse HEADER from above)
    HEADER = [
        "id",
        "site",
        "job_url",
        "job_url_direct",
        "title",
        "company",
        "location",
        "date_posted",
        "job_type",
        "salary_source",
        "interval",
        "min_amount",
        "max_amount",
        "currency",
        "is_remote",
        "job_level",
        "job_function",
        "listing_type",
        "emails",
        "description",
        "company_industry",
        "company_url",
        "company_logo",
        "company_url_direct",
        "company_addresses",
        "company_num_employees",
        "company_revenue",
        "company_description",
        "skills",
        "experience_range",
        "company_rating",
        "company_reviews_count",
        "vacancy_count",
        "work_from_home_type",
    ]
    for col in HEADER:
        if col == "id":
            continue
        if col not in df.columns:
            df[col] = ""

    # Reorder to match expected CSV (without id)
    df_out = df[[c for c in HEADER if c != "id"]].copy()
    return df_out
