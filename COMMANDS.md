## Discord Bot Commands (JobCord)

This document lists the slash commands exposed by the Discord bot, how to use them, and a few implementation notes and edge-cases to be aware of.

Notes:
- Commands are implemented as application (slash) commands and are registered via the bot's `bot.tree`.
- Some commands rely on data found in `src/data/developer_jobs.csv` and the local user DB `src/data/user_profiles.db`.
- A few commands require optional heavy dependencies (pandas). If those packages are not installed the bot will show a helpful message.

---

### /status
Description: Update a tracked job's application status, or list your tracked jobs.

Usage:
- `/status <job_id> <status>` — set the status for the job with id `job_id`.
- `/status list` — list your tracked jobs and their statuses.

Parameters:
- job_id: integer — the `id` column from `src/data/developer_jobs.csv`.
- status: one of `applied`, `denied`, `accepted`, `interview`.

Examples:
- `/status 123 applied` — mark job 123 as applied.
- `/status list` — show all jobs you have tracked.

Notes:
- This command uses `pandas` to read `src/data/developer_jobs.csv`. If pandas is not installed it will prompt you to install it (`pip install pandas`).
- If the provided `job_id` isn't present in `developer_jobs.csv` the command will tell you to use `/filter` or the job listing flow to find valid IDs.

---

### /filter
Description: Search jobs by keyword in titles or companies and return a short list of matching jobs.

Usage:
- `/filter <keyword>` — returns up to the top 5 matches and their links.

Parameters:
- keyword: string — e.g. `python`, `frontend`, `remote`.

Example:
- `/filter python` — find jobs that match “python”.

Notes:
- The command uses the project's scraping / search helpers which rely on `pandas` and the CSV job dataset. If required dependencies are missing you'll see a message recommending `pip install pandas`.
- The response includes short lines showing the Job ID (use that with `/status`), title, company, and a link.

---

### /profile_set
Description: Set your profile / job preferences (skills, location, seniority).

Usage:
- `/profile_set skills:<comma-separated> location:<string> seniority:<string>`

Examples:
- `/profile_set skills:python,django location:Remote seniority:senior`

Notes:
- Profiles are stored in `src/data/user_profiles.db` (SQLite). The bot will create the DB / table on init if you used the `init_db.py` helper.

---

### /profile_view
Description: View your stored profile (skills, location, seniority and whether alerts are enabled).

Usage:
- `/profile_view`

Notes:
- The command reads your profile from the SQLite DB and returns the stored values.

---

### /subscribe and /unsubscribe
Description: Toggle subscription to job notifications.

Usage:
- `/subscribe` — turn on job alert notifications for your profile (updates the DB).
- `/unsubscribe` — turn off job alert notifications.

Notes:
- These commands update the `subscribe_alerts` field in `src/data/user_profiles.db`.

---

### /add_source
Description: Add a custom company career page or a custom source URL so the scrapers can include it in future runs.

Usage:
- `/add_source <url>`

Example:
- `/add_source https://company.com/careers` — adds a custom careers page for the invoking user.

Notes:
- The command forwards the request to the project's custom-scraper helper. Depending on how you run scrapers the URL may be picked up on the next scrape run.

---

### /analyze
Description: Summarize a job description using the AI tool (OpenAI).

Usage:
- `/analyze <job_id>` — run an AI summarization for the job with the given id.

Parameters:
- job_id: integer — the job id in `src/data/developer_jobs.csv`.

Notes & Requirements:
- This command uses the `openai` package and will require an API key to be configured where the bot runs (e.g., an `OPENAI_API_KEY` environment variable or otherwise configured in your environment).
- The implementation uses the OpenAI Completion API; ensure you have the correct package version and credentials if you intend to use `/analyze`.

---

Developer notes & troubleshooting
- Command registration: after the bot starts, Discord can take a short while to register application commands globally (or per-guild). For development, consider using guild registration (faster) or allow a few minutes.
- Missing dependencies: If a command says it requires `pandas` or `bs4`, installing those packages in your bot environment will usually fix the issue:
  - pip install pandas beautifulsoup4
- Job data: The `developer_jobs.csv` file in `src/data/` is the canonical source of job IDs and details used by `/filter` and `/status`. If it's empty you will not be able to set statuses for jobs.
- DB initialization: Run the provided `init_db.py` helper (or `make run-local` which calls it) to create the `user_profiles.db` table before using `/profile_set` or subscription commands.
- OpenAI: Provide your OpenAI API key in the environment before starting the bot if you plan to use `/analyze`.

If anything here is unclear or you want the commands reworked (e.g., add per-guild dev-only variants, pagination UI, or more detailed examples), tell me which commands to improve and I will update the implementation and/or this doc.
