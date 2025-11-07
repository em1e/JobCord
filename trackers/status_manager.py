import pandas as pd
import os

STATUS_PATH = "src/data/job_status.csv"

def load_statuses():
    if os.path.exists(STATUS_PATH):
        return pd.read_csv(STATUS_PATH)
    else:
        return pd.DataFrame(columns=["id", "title", "company", "status"])

def save_statuses(df):
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    df.to_csv(STATUS_PATH, index=False)

def set_status(job_id, title, company, status):
    df = load_statuses()
    if job_id in df["id"].values:
        df.loc[df["id"] == job_id, "status"] = status
    else:
        new_entry = pd.DataFrame([[job_id, title, company, status]],
                                 columns=["id", "title", "company", "status"])
        df = pd.concat([df, new_entry], ignore_index=True)
    save_statuses(df)
    return df

def list_statuses():
    return load_statuses()