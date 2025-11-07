import asyncio
import logging

from discord_bot.bot import bot
import discord

from scraper.scrape_manager import scrape_all

logger = logging.getLogger(__name__)


@bot.tree.command(name="scrape", description="Run all scrapers now (manual trigger)")
async def scrape_cmd(interaction: discord.Interaction):
    """Manually run all scrapers and persist results to `src/data/developer_jobs.csv`.

    This runs the blocking `scrape_all()` call inside a thread so the bot event
    loop isn't blocked.
    """
    await interaction.response.defer(thinking=True)

    try:
        # Run the blocking scrape_all() in a thread.
        df = await asyncio.to_thread(scrape_all)
        try:
            count = len(df) if df is not None else 0
        except Exception:
            # df might not be a pandas DataFrame if things went wrong
            count = 0

        await interaction.followup.send(f"✅ Scrape finished. {count} jobs written to src/data/developer_jobs.csv")
    except ImportError as ie:
        logger.exception("Missing dependency while running manual scrape")
        await interaction.followup.send(
            "This scrape requires additional dependencies (pandas). Run `python scripts/scrape_now.py` or install pandas in the bot environment."
        )
    except Exception as e:
        logger.exception("Manual scrape failed")
        await interaction.followup.send(f"❌ Scrape failed: {e}")
