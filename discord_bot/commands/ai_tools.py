import openai
from scraper.scrape_manager import get_job_by_id

@bot.tree.command(name="analyze", description="Summarize a job description using AI")
async def analyze(interaction, job_id: int):
    job = get_job_by_id(job_id)
    prompt = f"Summarize the following developer job:\n{job['description']}"
    resp = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=150)
    await interaction.response.send_message(resp.choices[0].text)