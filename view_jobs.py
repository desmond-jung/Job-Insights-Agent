from functions.database import get_all_jobs
import json
from datetime import datetime

def format_job(job):
    """Format a job tuple into a dictionary with proper field names"""
    return {
        'job_id': job[0],
        'title': job[1],
        'company_name': job[2],
        'location': job[3],
        'industry': job[4],
        'description': job[5],
        'seniority_level': job[6],
        'employment_type': job[7],
        'job_function': job[8],
        'years_experience': job[9],
        'salary_range': job[10],
        'created_at': job[11]
    }

def main():
    # Get all jobs from database
    jobs = get_all_jobs()
    
    # Format jobs into dictionaries
    formatted_jobs = [format_job(job) for job in jobs]
    
    # Print summary
    print(f"\nFound {len(formatted_jobs)} jobs in database")
    
    # Print each job's details
    for i, job in enumerate(formatted_jobs, 1):
        print(f"\n{'='*80}")
        print(f"Job {i}:")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company_name']}")
        print(f"Location: {job['location']}")
        print(f"Industry: {job['industry']}")
        print(f"Seniority: {job['seniority_level']}")
        print(f"Employment Type: {job['employment_type']}")
        print(f"Job Function: {job['job_function']}")
        print(f"Years Experience: {job['years_experience']}")
        print(f"Salary Range: {job['salary_range']}")
        print(f"Created At: {job['created_at']}")
        print(f"\nDescription: {job['description'][:200]}...")  # First 200 chars of description
    
    # Save to JSON file for easier viewing
    with open('database_contents.json', 'w') as f:
        json.dump(formatted_jobs, f, indent=2, default=str)
    print(f"\nFull database contents saved to database_contents.json")

if __name__ == "__main__":
    main() 