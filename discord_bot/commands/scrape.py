import asyncio
import logging
import io
from typing import Optional

from discord_bot.bot import bot
import discord

# Use JobSky scraper when available; fall back to existing scrape_all for full-run
from storage.scrape_manager import scrape_all, append_jobs_dataframe
from storage.scrape_manager import scrape_watchlist
try:
    from jobsky import scrape_jobs
except Exception:
    scrape_jobs = None

from discord_bot.commands.profile import view_profile

logger = logging.getLogger(__name__)


@bot.tree.command(name="scrape", description="Run a job scrape for your profile or given parameters")
async def scrape_cmd(
    interaction: discord.Interaction,
    search_term: Optional[str] = None,
    location: Optional[str] = None,
    hours_old: Optional[int] = None,
    results_wanted: int = 15,
    sites: Optional[str] = None,  # comma-separated list of site names e.g. "indeed,linkedin"
    site: Optional[str] = None,  # alias for a single site (e.g. "watchlist")
):
    """Run a scrape for the invoking user.

    Parameters can be provided directly. If omitted, the user's profile
    (from `profile.view_profile`) will be used as a fallback for `search_term`
    and `location`.
    `sites` should be a comma-separated list (e.g. "indeed,linkedin,google").
    """
    await interaction.response.defer(thinking=True)

    # If JobSky's scrape_jobs is available, use it; otherwise run the legacy full scrape_all
    try:
        # Determine parameters: prefer explicit args, otherwise profile values
        profile = view_profile(str(interaction.user.id))
        profile_skills = profile[0] if profile else None
        profile_location = profile[1] if profile else None

        final_search = search_term or profile_skills
        final_location = location or profile_location

        # Accept either `sites` (comma-separated) or singular `site` as an alias.
        site_input = None
        if sites:
            site_input = sites
        elif site:
            site_input = site

        site_list = None
        if site_input:
            # allow comma-separated even in the singular alias
            site_list = [s.strip() for s in site_input.split(",") if s.strip()]

        if site_list and any(s.lower() == 'watchlist' for s in site_list):
            # Run only the watchlist-based scraping path
            df = await asyncio.to_thread(scrape_watchlist, results_wanted_per_item=results_wanted)
            # Append to canonical CSV
            try:
                await asyncio.to_thread(append_jobs_dataframe, df)
            except Exception:
                logger.exception("Failed to append watchlist results to developer_jobs.csv")
        elif scrape_jobs:
            # Run JobSky scrape with user parameters in a thread
            df = await asyncio.to_thread(
                scrape_jobs,
                site_name=site_list,
                search_term=final_search,
                location=final_location,
                hours_old=hours_old,
                results_wanted=results_wanted,
            )
            # Also append these results to the canonical developer_jobs.csv so
            # the repository keeps a growing record (do this in a thread).
            try:
                await asyncio.to_thread(append_jobs_dataframe, df)
            except Exception:
                logger.exception("Failed to append jobsky results to developer_jobs.csv")
        else:
            # Fallback: run existing manager which scrapes all sources and writes to file
            df = await asyncio.to_thread(scrape_all)

        try:
            count = len(df) if df is not None else 0
        except Exception:
            count = 0

        # If we have a DataFrame, attach it as CSV; otherwise just report count
        if df is not None and hasattr(df, "to_csv"):
            buf = io.BytesIO()
            # to_csv requires text bytes; write to string then encode
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            buf.write(csv_bytes)
            buf.seek(0)
            discord_file = discord.File(fp=buf, filename="jobs.csv")
            await interaction.followup.send(
                content=f"✅ Scrape finished. {count} jobs found.", file=discord_file
            )
        else:
            await interaction.followup.send(f"✅ Scrape finished. {count} jobs found.")

    except ImportError as ie:
        logger.exception("Missing dependency while running manual scrape")
        await interaction.followup.send(
            "This scrape requires additional dependencies (pandas). Run `python scripts/scrape_now.py` or install pandas in the bot environment."
        )
    except Exception as e:
        logger.exception("Manual scrape failed")
        await interaction.followup.send(f"❌ Scrape failed: {e}")
