from functions.database import get_all_jobs
import json
from datetime import datetime
if __name__ == "__main__":
    
    def format_job(job):
        """Format a job tuple into a dictionary with named fields"""
        return {
            "job_id": job[0],
            "title": job[1],
            "company_name": job[2],
            "location": job[3],
            "industry": job[4],
            "description": job[5],
            "created_at": job[6]
        }

    def main():
        # Get all jobs from database
        jobs = get_all_jobs()
        
        # Format jobs into dictionaries
        formatted_jobs = [format_job(job) for job in jobs]
        
        # Print summary
        print(f"\nFound {len(formatted_jobs)} jobs in database")
        
        # Save to JSON file
        output_file = "database_contents.json"
        with open(output_file, 'w') as f:
            json.dump(formatted_jobs, f, indent=2)
        print(f"\nDatabase contents saved to {output_file}")
        
        # Print first job as preview
        if formatted_jobs:
            print("\nPreview of first job:")
            print(json.dumps(formatted_jobs[0], indent=2))

if __name__ == "__main__":
    main() 