from discord_bot.bot import bot
import discord
from storage.custom_scraper import add_custom_source


@bot.tree.command(name="add_source", description="Add a custom company career page")
async def add_source(interaction: discord.Interaction, url: str):
    try:
        add_custom_source(str(interaction.user.id), url)
        await interaction.response.send_message(f"✅ Added custom source: {url}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to add custom source: {e}")