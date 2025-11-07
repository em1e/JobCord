from discord_bot.bot import bot
import sqlite3


DB_PATH = "src/data/user_profiles.db"

def set_subscribe(discord_id, value: bool):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE user_profiles SET subscribe_alerts=? WHERE discord_id=?", (1 if value else 0, discord_id))
    conn.commit()
    conn.close()

@bot.tree.command(name="subscribe", description="Subscribe to job notifications")
async def subscribe(interaction):
    set_subscribe(str(interaction.user.id), True)
    await interaction.response.send_message("✅ Subscribed to job alerts!")

@bot.tree.command(name="unsubscribe", description="Unsubscribe from job notifications")
async def unsubscribe(interaction):
    set_subscribe(str(interaction.user.id), False)
    await interaction.response.send_message("❌ Unsubscribed from job alerts")