import os
import sqlite3

DB_DIR = os.path.join("src", "data")
DB_PATH = os.path.join(DB_DIR, "user_profiles.db")

def ensure_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles(
            discord_id TEXT PRIMARY KEY,
            skills TEXT,
            location TEXT,
            seniority TEXT,
            subscribe_alerts INTEGER DEFAULT 1
        )
        """
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_db()
    print(f"Initialized DB at {DB_PATH}")
