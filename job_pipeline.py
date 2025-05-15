from functions.scraper import scrape_jobs
from functions.database import init_db, store_jobs, clear_jobs

def main():
    # Initialize database
    init_db()
    
    # Clear existing jobs
    clear_jobs()
    
    # Scrape recent jobs from LinkedIn
    print("Scraping recent jobs from LinkedIn...")
    jobs = scrape_jobs(num_jobs=50)  # Adjust number as needed
    
    # Store jobs in database
    print(f"Storing {len(jobs)} jobs in database...")
    for job in jobs:
        store_jobs(job)
    
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main()