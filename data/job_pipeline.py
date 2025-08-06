from scraper import scrape_jobs
from database import init_db, store_jobs, clear_jobs
import time

def main(clear_existing=False):
    start_time = time.time()
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Optionally clear existing jobs
        if clear_existing:
            print("Clearing existing jobs...")
            clear_jobs()
        else:
            print("Keeping existing jobs...")
        
        # Scrape recent jobs from LinkedIn
        print("Scraping recent jobs from LinkedIn...")
        jobs = scrape_jobs(num_jobs=25)  # Increased to 50 jobs
        
        if not jobs:
            print("No jobs were scraped. Check if LinkedIn is blocking the requests.")
            return
            
        # Store jobs in database
        print(f"Storing {len(jobs)} jobs in database...")
        successful_stores = 0
        failed_stores = 0
        
        for job in jobs:
            try:
                store_jobs(job)
                successful_stores += 1
                #print(f"Successfully stored job {job.get('job_id')} - {job.get('title')}")
            except Exception as e:
                failed_stores += 1
                #print(f"Failed to store job {job.get('job_id')}: {str(e)}")
        end_time = time.time()
        print(f"\nPipeline completed!")
        print(f"Total jobs scraped: {len(jobs)}")
        print(f"Successfully stored: {successful_stores}")
        print(f"Failed to store: {failed_stores}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")

if __name__ == "__main__":
    main()