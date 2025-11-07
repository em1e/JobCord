from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from storage.scrape_manager import scrape_all, get_new_jobs
from bot.discord_bot import TOKEN  # or use webhook
import requests, os

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def daily_notify():
    scrape_all()
    new_jobs = get_new_jobs()
    if not new_jobs.empty:
        webhook = os.getenv("DISCORD_WEBHOOK_URL")
        for _, job in new_jobs.iterrows():
            msg = {
                "content": f"💼 **{job['title']}** at **{job['company']}** ({job['source']})\n🔗 {job['link']}"
            }
            requests.post(webhook, json=msg)

with DAG(
    "daily_job_alerts",
    default_args=default_args,
    description="Scrape and notify daily about new jobs",
    schedule_interval="@daily",
    start_date=datetime(2025, 10, 22),
    catchup=False,
) as dag:
    notify_task = PythonOperator(
        task_id="daily_discord_job_alert",
        python_callable=daily_notify,
    )