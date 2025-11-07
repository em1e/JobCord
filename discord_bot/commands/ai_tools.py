import openai
from discord_bot.bot import bot
import discord
from storage.scrape_manager import get_job_by_id
import logging

logger = logging.getLogger(__name__)


@bot.tree.command(name="analyze", description="Summarize a job description using AI")
async def analyze(interaction: discord.Interaction, job_id: int):
    await interaction.response.defer(thinking=True)
    job = get_job_by_id(job_id)
    if not job:
        await interaction.followup.send(f"❌ Job with id `{job_id}` not found.")
        return

    prompt = f"Summarize the following developer job:\n{job.get('description', job.get('title', ''))}"
    try:
        resp = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=150)
        text = resp.choices[0].text if hasattr(resp, 'choices') and resp.choices else str(resp)
        await interaction.followup.send(text)
    except Exception as e:
        logger.exception("OpenAI request failed in /analyze")
        await interaction.followup.send("⚠️ Failed to analyze the job. Check OpenAI configuration and try again.")