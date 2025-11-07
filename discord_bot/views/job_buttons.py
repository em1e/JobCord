import discord
from trackers.status_manager import set_status

class JobButtons(discord.ui.View):
    def __init__(self, job_id, title, company):
        super().__init__()
        self.job_id = job_id
        self.title = title
        self.company = company

    @discord.ui.button(label="Mark as Applied", style=discord.ButtonStyle.green)
    async def mark_applied(self, interaction, button):
        set_status(self.job_id, self.title, self.company, "applied")
        await interaction.response.send_message("✅ Status set to applied!", ephemeral=True)

    @discord.ui.button(label="Open Link", style=discord.ButtonStyle.link, url="https://example.com")
    async def open_link(self, interaction, button):
        pass