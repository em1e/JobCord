from scraper.custom_scraper import add_custom_source

@bot.tree.command(name="add_source", description="Add a custom company career page")
async def add_source(interaction, url: str):
    add_custom_source(str(interaction.user.id), url)
    await interaction.response.send_message(f"✅ Added custom source: {url}")