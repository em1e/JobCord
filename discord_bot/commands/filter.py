from discord_bot.bot import bot
import discord
from discord import app_commands
import logging
from storage.scrape_manager import filter_jobs

logger = logging.getLogger(__name__)


@bot.tree.command(
    name="filter",
    description="Filter jobs by keyword (e.g., /filter python)"
)
@app_commands.describe(
    keyword="Keyword to search in job titles or companies."
)
async def filter_jobs_cmd(interaction: discord.Interaction, keyword: str):
    """Find jobs matching `keyword` and return up to 5 top results.

    Improved error handling:
    - If pandas (or other optional deps) is missing: tell the user to install pandas.
    - If another unexpected error happens: log it and return a short error message.
    """
    await interaction.response.defer(thinking=True)
    try:
        df = filter_jobs(keyword)
    except ImportError as ie:
        # Likely pandas or similar missing from the environment
        logger.exception("Missing dependency when running /filter")
        await interaction.followup.send(
            "This command requires additional dependencies (pandas). Install them with `pip install pandas` to use `/filter`."
        )
        return
    except Exception as e:
        # Unexpected error: log full traceback and send concise message to user
        logger.exception("Unexpected error in /filter command")
        await interaction.followup.send(
            f"An unexpected error occurred while searching for `{keyword}`."
        )
        return

    if df is None or getattr(df, "empty", True):
        await interaction.followup.send(f"No results found for `{keyword}`.")
        return

    latest = df.head(5)

    response = "\n\n".join([
        f"🆔 `{int(row.id)}` | 💼 **{row.title}** at **{row.company}** ({row.source})\n🔗 {row.link}"
        for _, row in latest.iterrows()
    ])

    await interaction.followup.send(f"Found {len(df)} matches for `{keyword}`:\n\n{response}")