import sqlite3
from datetime import datetime
import json

def init_db():
    """Initialize the database and create tables if they don't exist"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    print(f"📁 Initializing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop existing table if it exists
    c.execute('DROP TABLE IF EXISTS jobs')

    # Create table with current schema
    c.execute('''
        CREATE TABLE jobs(
            job_id TEXT PRIMARY KEY,
            job_url TEXT,
            source TEXT,
            title TEXT,
            company_name TEXT,
            description TEXT,
            location TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            remote TEXT,
            industry TEXT,
            seniority_level TEXT,
            employment_type TEXT,
            job_function TEXT,
            salary_raw TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            salary_avg DECIMAL,
            yoe_raw TEXT,
            yoe_min INTEGER,
            yoe_max INTEGER,
            yoe_avg DECIMAL,
            education TEXT,
            skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add indexes for common queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_company ON jobs(company_name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)')

    conn.commit()
    conn.close()

def store_job(job_id, job_url, source, title, company_name, description, location, city, state, country, 
              remote, industry, seniority_level, employment_type, job_function, salary_raw, salary_min, 
              salary_max, salary_avg, yoe_raw, yoe_min, yoe_max, yoe_avg, education, skills):
    """Store a single job in the database"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Convert lists to JSON strings if they are lists
        if isinstance(education, list):
            education = json.dumps(education)
        if isinstance(skills, list):
            skills = json.dumps(skills)
        
        c.execute('''
            INSERT INTO jobs (job_id, job_url, source, title, company_name, location, city, state, country, remote,
                            industry, description, seniority_level, employment_type, job_function, 
                            salary_raw, salary_min, salary_max, salary_avg, yoe_raw, yoe_min, yoe_max, yoe_avg, 
                            education, skills) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id, job_url, source, title, company_name, location, city, state, country, remote,
            industry, description, seniority_level, employment_type, job_function,
            salary_raw, salary_min, salary_max, salary_avg, yoe_raw, yoe_min, yoe_max, yoe_avg,
            education, skills
        ))
        
        conn.commit()
        return True
        
    except sqlite3.IntegrityError:
        # Job already exists
        return False
    except Exception as e:
        print(f"Error storing job: {e}")
        return False
    finally:
        conn.close()

def store_jobs(job_data):
    """Store a job in the database
    
    Args:
        job_data (dict): Dictionary containing job information
    """
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Convert lists to JSON strings
        education = json.dumps(job_data.get('education', []))
        skills = json.dumps(job_data.get('skills', []))
        
        c.execute('''
            INSERT INTO jobs (job_id, job_url, source, title, company_name, location, city, state, country, remote,
                            industry, description, seniority_level, employment_type, job_function, 
                            salary_raw, salary_min, salary_max, salary_avg, yoe_raw, yoe_min, yoe_max, yoe_avg, 
                            education, skills) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data.get('job_id'),
            job_data.get('job_url'),
            job_data.get('source'),
            job_data.get('title'),
            job_data.get('company_name'),
            job_data.get('location'),
            job_data.get('city'),
            job_data.get('state'),
            job_data.get('country'),
            job_data.get('remote'),
            job_data.get('industry'),
            job_data.get('description'),
            job_data.get('seniority_level'),
            job_data.get('employment_type'),
            job_data.get('job_function'),
            job_data.get('salary_raw'),
            job_data.get('salary_min'),
            job_data.get('salary_max'),
            job_data.get('salary_avg'),
            job_data.get('yoe_raw'),
            job_data.get('yoe_min'),
            job_data.get('yoe_max'),
            job_data.get('yoe_avg'),
            education,  # Now using JSON string
            skills     # Now using JSON string
        ))
        conn.commit()
        print(f"Successfully stored job {job_data.get('job_id')}")
    except sqlite3.IntegrityError:
        print(f"Job {job_data.get('job_id')} already exists in database")
    except Exception as e:
        print(f"Error storing job {job_data.get('job_id')}: {str(e)}")
    finally:
        conn.close()

def clear_jobs():
    """Delete all jobs from the database."""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM jobs')
    conn.commit()
    conn.close()

def get_all_jobs():
    """Retrieve all jobs from the database."""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT * FROM jobs')
    jobs = c.fetchall()
    
    conn.close()
    return jobs

def get_job_by_id(job_id):
    """Retrieve a specific job by its ID."""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
    job = c.fetchone()
    
    if job:
        # Get column names
        c.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in c.fetchall()]
        
        # Convert to dictionary
        job_dict = {}
        for i, col in enumerate(columns):
            # Convert JSON strings back to Python objects
            if col in ['education', 'skills'] and job[i]:
                try:
                    job_dict[col] = json.loads(job[i])
                except:
                    job_dict[col] = job[i]
            else:
                job_dict[col] = job[i]
        
        conn.close()
        return job_dict
    
    conn.close()
    return None

def search_jobs(title=None, location=None, num_jobs=5):
    """Search jobs in the database by title and location"""
    print(f"🔍 search_jobs called with: title='{title}', location='{location}', num_jobs={num_jobs}")
    
    # Get the absolute path to the database file
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get all jobs
    c.execute('SELECT * FROM jobs')
    jobs = c.fetchall()
    print(f"📊 Total jobs in database: {len(jobs)}")
    
    # Get column names
    c.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in c.fetchall()]
    
    # Convert to list of dictionaries
    job_dicts = []
    for row in jobs:
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
        job_dicts.append(job)
    
    # Filter jobs based on title and location
    filtered_jobs = []
    
    for job in job_dicts:
        job_title = job.get('title', '').lower()
        job_location = job.get('location', '').lower()
        
        # Check title match (if title is provided, it must match)
        title_match = not title or title == 'None' or (title and title.lower() in job_title)
        
        # Check location match (if location is provided, it must match)
        location_match = not location or location == 'None' or (location and location.lower() in job_location)
        
        if title_match and location_match:
            filtered_jobs.append(job)
            if len(filtered_jobs) >= num_jobs:
                break
    
    conn.close()
    return filtered_jobs

def get_job_statistics(days_back=7, title_filter=None):
    """Get comprehensive statistics about jobs in the database"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get total job count
    c.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = c.fetchone()[0]
    
    # Get recent jobs (last X days)
    c.execute('''
        SELECT COUNT(*) FROM jobs 
        WHERE created_at >= datetime('now', '-{} days')
    '''.format(days_back))
    recent_jobs = c.fetchone()[0]
    
    # Get top companies
    c.execute('''
        SELECT company_name, COUNT(*) as job_count 
        FROM jobs 
        GROUP BY company_name 
        ORDER BY job_count DESC 
        LIMIT 10
    ''')
    top_companies = c.fetchall()
    
    # Get top locations
    c.execute('''
        SELECT location, COUNT(*) as job_count 
        FROM jobs 
        WHERE location IS NOT NULL AND location != ''
        GROUP BY location 
        ORDER BY job_count DESC 
        LIMIT 10
    ''')
    top_locations = c.fetchall()
    
    # Get employment types
    c.execute('''
        SELECT employment_type, COUNT(*) as job_count 
        FROM jobs 
        WHERE employment_type IS NOT NULL AND employment_type != ''
        GROUP BY employment_type 
        ORDER BY job_count DESC
    ''')
    employment_types = c.fetchall()
    
    # Get remote vs onsite
    c.execute('''
        SELECT 
            CASE 
                WHEN remote = '1' OR LOWER(location) LIKE '%remote%' THEN 'Remote'
                ELSE 'On-site'
            END as work_type,
            COUNT(*) as job_count
        FROM jobs 
        GROUP BY work_type
    ''')
    work_types = c.fetchall()
    
    # Get jobs by title filter if provided
    title_stats = {}
    if title_filter:
        c.execute('''
            SELECT COUNT(*) FROM jobs 
            WHERE LOWER(title) LIKE LOWER(?)
        ''', (f'%{title_filter}%',))
        title_stats['count'] = c.fetchone()[0]
        title_stats['filter'] = title_filter
    
    conn.close()
    
    return {
        'total_jobs': total_jobs,
        'recent_jobs': recent_jobs,
        'days_back': days_back,
        'top_companies': [{'company': company, 'count': count} for company, count in top_companies],
        'top_locations': [{'location': location, 'count': count} for location, count in top_locations],
        'employment_types': [{'type': emp_type, 'count': count} for emp_type, count in employment_types],
        'work_types': [{'type': work_type, 'count': count} for work_type, count in work_types],
        'title_stats': title_stats
    }

if __name__ == "__main__":
    # Test the search_jobs function
    print("🧪 Testing search_jobs function...")
    
    # Test 1: Search for software engineer jobs
    results = search_jobs(title="Director of Operations", location="United States")
    print(results)
    for i, job in enumerate(results, 1):
        print(f"  {i}. {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}")
    
    # # Test 2: Search for remote jobs
    # print("\n2. Searching for 'remote' jobs:")
    # results = search_jobs(location="remote", num_jobs=3)
    # print(f"Found {len(results)} jobs")
    # for i, job in enumerate(results, 1):
    #     print(f"  {i}. {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}")
    
    # # Test 3: Search for all jobs (no filters)
    # print("\n3. Searching for all jobs (no filters):")
    # results = search_jobs(num_jobs=5)
    # print(f"Found {len(results)} jobs")
    # for i, job in enumerate(results, 1):
    #     print(f"  {i}. {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}")
    
    # print("\n✅ Database search tests completed!")