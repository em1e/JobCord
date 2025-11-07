from discord_bot.bot import bot
from trackers.status_manager import set_status, list_statuses

VALID_STATUSES = ["applied", "denied", "accepted", "interview"]

@bot.tree.command(name="status", description="Update or list job application statuses.")
async def status_cmd(interaction, job_id: int = None, status: str = None):
    await interaction.response.defer(thinking=True)
    try:
        import pandas as pd
    except Exception:
        await interaction.followup.send(
            "This command requires `pandas`. Install it with `pip install pandas` to use `/status`."
        )
        return

    df = pd.read_csv("src/data/developer_jobs.csv")

    if status == "list" or (job_id is None and status == "list"):
        statuses = list_statuses()
        if statuses.empty:
            await interaction.followup.send("You haven’t tracked any jobs yet.")
            return
        msg = "\n".join([
            f"🆔 {int(row.id)} | **{row.title}** at **{row.company}** → `{row.status}`"
            for _, row in statuses.iterrows()
        ])
        await interaction.followup.send(f"📋 **Your Tracked Jobs:**\n{msg}")
        return

    if job_id is None or status not in VALID_STATUSES:
        await interaction.followup.send(
            f"Usage: `/status <job_id> <status>` where status ∈ {VALID_STATUSES}, "
            "or `/status list` to view all."
        )
        return

    if job_id not in df["id"].values:
        await interaction.followup.send(f"❌ Job ID `{job_id}` not found. Use `/jobs` or `/filter` to see valid IDs.")
        return

    job = df[df["id"] == job_id].iloc[0]
    set_status(job_id, job['title'], job['company'], status)
    await interaction.followup.send(
        f"✅ Updated status for **{job['title']}** at **{job['company']}** → `{status}`"
    )