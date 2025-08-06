import sqlite3
import json
from datetime import datetime

def check_database():
    """Check the database contents and provide statistics"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM jobs")
    total_count = c.fetchone()[0]
    
    print(f"📊 Database Statistics:")
    print(f"Total jobs in database: {total_count}")
    conn.close()

def view_database():
    """View all contents of the jobs database in a readable format"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get column names
    c.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in c.fetchall()]
    
    # Get all rows
    c.execute("SELECT * FROM jobs")
    rows = c.fetchall()
    
    # Convert to list of dictionaries
    jobs = []
    for row in rows:
        job = {}
        for i, col in enumerate(columns):
            # Convert JSON strings back to Python objects
            if col in ['education', 'skills'] and row[i]:
                try:
                    job[col] = json.loads(row[i])
                except:
                    job[col] = row[i]
            else:
                job[col] = row[i]
        jobs.append(job)
    
    # Print in a readable format
    print(f"\nFound {len(jobs)} jobs in database:")
    print("=" * 80)
    
    for i, job in enumerate(jobs, 1):
        print(f"\nJob {i}:")
        for key, value in job.items():
            if key != 'description':  # Skip full description to keep output clean
                print(f"{key}: {value}")
        print("-" * 40)
    
    # Save to JSON file for easier viewing
    import os
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database_contents.json')
    with open(json_path, 'w') as f:
        json.dump(jobs, f, indent=2, default=str)
    print(f"\nFull database contents saved to {json_path}")
    
    conn.close()

if __name__ == "__main__":
   check_database()