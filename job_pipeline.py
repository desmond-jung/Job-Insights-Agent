from functions.scraper import scrape_jobs
from functions.database import init_db, store_jobs, clear_jobs
import time

def main():
    start_time = time.time()
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Clear existing jobs
        print("Clearing existing jobs...")
        clear_jobs()
        
        # Scrape recent jobs from LinkedIn
        print("Scraping recent jobs from LinkedIn...")
        jobs = scrape_jobs(num_jobs=50)  # Adjust number as needed
        
        # Store jobs in database
        print(f"Storing {len(jobs)} jobs in database...")
        successful_stores = 0
        for job in jobs:
            try:
                store_jobs(job)
                successful_stores += 1
            except Exception as e:
                print(f"Failed to store job {job.get('job_id')}: {str(e)}")
        
        end_time = time.time()
        print(f"\nPipeline completed!")
        print(f"Total jobs scraped: {len(jobs)}")
        print(f"Successfully stored: {successful_stores}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")

if __name__ == "__main__":
    main()