from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route("/dashboard")
def dashboard():
    statuses = pd.read_csv("src/data/job_status.csv")
    jobs = pd.read_csv("src/data/developer_jobs.csv")

    status_counts = statuses['status'].value_counts().to_dict()
    source_counts = jobs['source'].value_counts().to_dict()

    return render_template(
        "dashboard.html",
        status_counts=status_counts,
        source_counts=source_counts
    )

if __name__ == "__main__":
    app.run(debug=True)