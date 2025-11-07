from discord.ext import pages

def create_job_pages(jobs_df):
    embeds = []
    for _, row in jobs_df.iterrows():
        embed = discord.Embed(title=row['title'], description=f"{row['company']} ({row['source']})", url=row['link'])
        embed.add_field(name="Job ID", value=str(row['id']))
        embeds.append(embed)
    paginator = pages.Paginator(pages=embeds, use_default_buttons=True)
    return paginator