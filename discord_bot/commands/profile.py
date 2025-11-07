from discord_bot.bot import bot
import sqlite3

DB_PATH = "src/data/user_profiles.db"

def set_profile(discord_id, skills=None, location=None, seniority=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_profiles(discord_id) VALUES(?)", (discord_id,))
    if skills:
        c.execute("UPDATE user_profiles SET skills=? WHERE discord_id=?", (skills, discord_id))
    if location:
        c.execute("UPDATE user_profiles SET location=? WHERE discord_id=?", (location, discord_id))
    if seniority:
        c.execute("UPDATE user_profiles SET seniority=? WHERE discord_id=?", (seniority, discord_id))
    conn.commit()
    conn.close()

def view_profile(discord_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT skills, location, seniority, subscribe_alerts FROM user_profiles WHERE discord_id=?", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result

# Discord commands
@bot.tree.command(name="profile_set", description="Set your job preferences")
async def profile_set(interaction, skills: str = None, location: str = None, seniority: str = None):
    set_profile(str(interaction.user.id), skills, location, seniority)
    await interaction.response.send_message("✅ Profile updated!")

@bot.tree.command(name="profile_view", description="View your job preferences")
async def profile_view(interaction):
    profile = view_profile(str(interaction.user.id))
    await interaction.response.send_message(
        f"📋 Skills: {profile[0]}, Location: {profile[1]}, Seniority: {profile[2]}, Alerts: {'On' if profile[3] else 'Off'}"
    )