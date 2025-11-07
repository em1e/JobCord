from typing import Optional
from discord_bot.bot import bot
import discord

from storage.watchlist import add_watchlist, view_watchlist, remove_watchlist


@bot.tree.command(name="watchlist_add", description="Add a company/job page to the scrape watchlist")
async def watchlist_add(interaction: discord.Interaction, url: str, note: Optional[str] = None):
    # Defer early to give the bot time to process IO
    await interaction.response.defer(thinking=True)
    try:
        # Basic validation of the provided URL
        if not isinstance(url, str) or not url.startswith("http"):
            await interaction.followup.send("❌ Please provide a valid URL starting with http:// or https://")
            return

        add_watchlist(url, note)

        # Provide feedback with the current watchlist length
        items = view_watchlist()
        count = len(items) if items is not None else "unknown"
        await interaction.followup.send(f"✅ Added to watchlist: {url} (total items: {count})")
    except Exception as e:
        # Log to console for debugging and provide a helpful error to the user
        try:
            print(f"watchlist_add error: {e}")
        except Exception:
            pass
        await interaction.followup.send(f"❌ Failed to add watchlist URL — check bot logs for details")


@bot.tree.command(name="watchlist_view", description="View current watchlist entries")
async def watchlist_view(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    try:
        items = view_watchlist()
        if not items:
            await interaction.followup.send("Watchlist is empty.")
            return
        lines = [f"{i}: {it.get('url')} — {it.get('note','')}" for i, it in enumerate(items)]
        await interaction.followup.send("\n".join(lines))
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to load watchlist: {e}")


@bot.tree.command(name="watchlist_rm", description="Remove a watchlist entry by index")
async def watchlist_rm(interaction: discord.Interaction, index: int):
    await interaction.response.defer(thinking=True)
    try:
        ok = remove_watchlist(index)
        if ok:
            await interaction.followup.send(f"✅ Removed watchlist item {index}")
        else:
            await interaction.followup.send(f"❌ No watchlist item at index {index}")
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to remove watchlist item: {e}")
