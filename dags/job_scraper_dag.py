from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from storage.scrape_manager import scrape_all, get_new_jobs
from trackers.profile_manager import get_subscribed_users
from discord_bot.bot import send_discord_message
default_args = {
    "owner": "jobcord",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def scrape_and_notify():
    df = scrape_all()

    new_jobs = get_new_jobs()
    if new_jobs.empty:
        print("No new jobs found today.")
        return

    print(f"🚀 Found {len(new_jobs)} new jobs!")

    users = get_subscribed_users()
    for _, job in new_jobs.iterrows():
        for user in users:
            if any(skill.lower() in job['title'].lower() for skill in (user.skills or "").split(',')):
                send_discord_message(user.discord_id, job)

with DAG(
    "jobcord_scraper",
    default_args=default_args,
    description="Scrapes jobs and sends new ones to Discord",
    schedule_interval="0 */6 * * *",
    start_date=datetime(2025, 10, 22),
    catchup=False,
    tags=["jobs", "discord", "automation"],
) as dag:

    job_alert_task = PythonOperator(
        task_id="scrape_and_notify",
        python_callable=scrape_and_notify,
    )

    job_alert_task