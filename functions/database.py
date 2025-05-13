import sqlite3
from datetime import datetime

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY,
            title TEXT,
            company_name TEXT,
            location TEXT,
            description TEXT,
            seniority_level TEXT,
            employment_type TEXT,
            job_function TEXT,
            industry TEXT,
            salary TEXT,
            yoe TEXT,
            education TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP  
        )
    ''')

    conn.commit()
    conn.close()    

def store_jobs(job_list):
    """Store a list of jobs in the database"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    current_time = datetime.now().isoformat()
    for job in job_list:
        c.execute('''
            INSERT OR REPLACE INTO jobs(
                id, title, company_name, location, description, 
                seniority_level, employment_type, job_function,
                industry, salary, yoe, education, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job['id'],
            job['title'],
            job['company_name'],
            job['location'],
            job['description'],
            job.get('seniority_level'),
            job.get('employment_type'),
            job.get('job_function'),
            job.get('industry'),
            job.get('salary'),
            job.get('yoe'),
            job.get('education'),
            current_time,
            current_time
        ))
  
    conn.commit()
    conn.close()
def list_all_jobs():
    """Retrieve all jobs from database"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    c.execute('''
        SELECT id, title, company_name, location, description, 
               seniority_level, employment_type, job_function,
               industry, salary, yoe, education, created_at, updated_at 
        FROM jobs
        ORDER BY created_at DESC
    ''')

    jobs = c.fetchall()
    conn.close()

    # Convert to list of dictionaries
    job_list = []
    for job in jobs:
        job_dict = {
            'id': job[0],
            'title': job[1],
            'company_name': job[2],
            'location': job[3],
            'description': job[4],
            'seniority_level': job[5],
            'employment_type': job[6],
            'job_function': job[7],
            'industry': job[8],
            'salary': job[9],
            'yoe': job[10],
            'education': job[11],
            'created_at': job[12],
            'updated_at': job[13]
        }
        job_list.append(job_dict)
    
    return job_list
def get_job_by_id(job_id):
    """Retrieve a job by its ID"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = c.fetchone()
    
    if job:
        job_dict = {
            'id': job[0],
            'title': job[1],
            'company_name': job[2],
            'location': job[3],
            'description': job[4],
            'seniority_level': job[5],
            'employment_type': job[6],
            'job_function': job[7],
            'industry': job[8],
            'salary': job[9],
            'yoe': job[10],
            'education': job[11],
            'created_at': job[12],
            'updated_at': job[13]
        }
        
        conn.close()
        return job_dict
    
    conn.close()
    return None