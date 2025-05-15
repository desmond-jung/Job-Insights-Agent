import sqlite3
from datetime import datetime
import json

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs(
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company_name TEXT,
            location TEXT,
            industry TEXT,
            description TEXT,
            seniority_level TEXT,
            employment_type TEXT,
            job_function TEXT,
            years_experience INTEGER,
            salary_range TEXT,
            required_skills TEXT,
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

    try:
        # Convert required_skills list to JSON string if it exists
        required_skills = json.dumps(job_data.get('required_skills')) if job_data.get('required_skills') else None
        
        c.execute('''
            INSERT INTO jobs (job_id, title, company_name, location, industry, description, seniority_level, employment_type, job_function, years_experience, salary_range, required_skills) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data.get('job_id'),
            job_data.get('title'),
            job_data.get('company_name'),
            job_data.get('location'),
            job_data.get('industry'),
            job_data.get('description'),
            job_data.get('seniority_level'),
            job_data.get('employment_type'),
            job_data.get('job_function'),
            job_data.get('years_experience'),
            job_data.get('salary_range'),
            required_skills
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Job {job_data.get('job_id')} already exists in database")
    except Exception as e:
        print(f"Error storing job: {str(e)}")
    finally:
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