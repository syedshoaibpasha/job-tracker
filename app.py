from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(jobs)")
    columns = [column[1] for column in cursor.fetchall()]

    if "application_date" not in columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN application_date TEXT"
        )

    if "job_link" not in columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN job_link TEXT"
        )

    if "notes" not in columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN notes TEXT"
        )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    search = request.args.get("search", "")
    status = request.args.get("status", "")

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    parameters = []

    if search:
        query += " AND (company LIKE ? OR role LIKE ?)"
        search_value = "%" + search + "%"
        parameters.extend([search_value, search_value])

    if status:
        query += " AND status = ?"
        parameters.append(status)

    cursor.execute(query, parameters)
    jobs = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Applied'")
    applied_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Interview'")
    interview_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Selected'")
    selected_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Rejected'")
    rejected_jobs = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        jobs=jobs,
        search=search,
        status=status,
        total_jobs=total_jobs,
        applied_jobs=applied_jobs,
        interview_jobs=interview_jobs,
        selected_jobs=selected_jobs,
        rejected_jobs=rejected_jobs
    )


@app.route("/add", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        status = request.form["status"]
        application_date = request.form["application_date"]
        job_link = request.form["job_link"]
        notes = request.form["notes"]

        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO jobs
            (company, role, status, application_date, job_link, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                role,
                status,
                application_date,
                job_link,
                notes
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_job.html")


@app.route("/delete/<int:job_id>")
def delete_job(job_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM jobs WHERE id = ?",
        (job_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        status = request.form["status"]
        application_date = request.form["application_date"]
        job_link = request.form["job_link"]
        notes = request.form["notes"]

        cursor.execute(
            """
            UPDATE jobs
            SET company = ?,
                role = ?,
                status = ?,
                application_date = ?,
                job_link = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                company,
                role,
                status,
                application_date,
                job_link,
                notes,
                job_id
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    )

    job = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_job.html",
        job=job
    )
init_db()

if __name__ == "__main__":
    app.run(debug=True)