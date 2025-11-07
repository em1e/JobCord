import discord

def create_job_pages(jobs_df):
    """Create a list of `discord.Embed` objects from a jobs DataFrame.

    Note: we intentionally return a list of embeds (not a Paginator) so the
    project does not depend on external paginator packages. Callers can send
    the embeds in whatever pagination UI they prefer.
    """
    embeds = []
    for _, row in jobs_df.iterrows():
        embed = discord.Embed(
            title=row.get('title', ''),
            description=f"{row.get('company', '')} ({row.get('source', '')})",
            url=row.get('link', None),
        )
        embed.add_field(name="Job ID", value=str(row.get('id', '')))
        embeds.append(embed)
    return embeds