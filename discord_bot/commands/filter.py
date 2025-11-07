from discord_bot.bot import bot
from discord.ext import commands
from discord import app_commands
from scraper.scrape_manager import filter_jobs
import pandas as pd

@bot.tree.command(
    name="filter",
    description="Filter jobs by keyword (e.g., /filter python)"
)
@app_commands.describe(
    keyword="Keyword to search in job titles or companies."
)
async def filter_jobs_cmd(interaction: commands.Context, keyword: str):
    await interaction.response.defer(thinking=True)
    
    df = filter_jobs(keyword)
    if df.empty:
        await interaction.followup.send(f"No results found for `{keyword}`.")
        return
    latest = df.head(5)

    response = "\n\n".join([
        f"🆔 `{int(row.id)}` | 💼 **{row.title}** at **{row.company}** ({row.source})\n🔗 {row.link}"
        for _, row in latest.iterrows()
    ])

    await interaction.followup.send(f"Found {len(df)} matches for `{keyword}`:\n\n{response}")