import sqlite3
import pandas as pd

def check_jobs():
    db_file = "linkedin_jobs.db"
    try:
        conn = sqlite3.connect(db_file)
        # Using pandas for a clean output
        df = pd.read_sql_query("SELECT job_id, title, company, location, scraped_at FROM scraped_jobs ORDER BY scraped_at DESC LIMIT 10", conn)
        if not df.empty:
            print("Successfully found jobs in the database. Here are the 10 most recent:")
            print(df)
        else:
            print("No jobs found in the 'scraped_jobs' table.")
    except Exception as e:
        print(f"An error occurred while querying the database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_jobs() 