import sqlite3
from datetime import datetime

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs(
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company_name TEXT,
            location TEXT,
            industry TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()    

def store_jobs(job_data):
    """Store a job in the database
    
    Args:
        job_data (dict): Dictionary containing job information
    """
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO jobs (title, company_name, location, industry, description) 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        job_data.get('title'),
        job_data.get('company_name'),
        job_data.get('location'),
        job_data.get('industry'),
        job_data.get('description')
    ))
    conn.commit()
    conn.close()

def clear_jobs():
    """Delete all jobs from the database."""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('DELETE FROM jobs')
    conn.commit()
    conn.close()

def get_all_jobs():
    """Retrieve all jobs from the database."""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM jobs')
    jobs = c.fetchall()
    
    conn.close()
    return jobs