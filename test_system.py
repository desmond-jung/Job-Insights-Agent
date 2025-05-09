# test_system.py
import os
from functions.orchestrator import orchestrator
from functions.scraper import scrape_jobs
from functions.embedder import embed_jobs
from functions.vector_store import build_faiss_index
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("\nJob Search System")
    print("=" * 50)
    
    while True:
        # Get user input
        job_title = input("\nEnter job title to search (or 'quit' to exit): ").strip()
        
        if job_title.lower() in ['quit', 'exit']:
            print("\nExiting program. Goodbye!")
            break
            
        location = input("Enter location (press Enter to skip): ").strip()
        num_jobs = input("Enter number of jobs to fetch (default: 5): ").strip()
        
        # Set default values
        if not num_jobs:
            num_jobs = 5
        else:
            try:
                num_jobs = int(num_jobs)
            except ValueError:
                print("Invalid number. Using default of 5 jobs.")
                num_jobs = 5
        
        # Construct the search query
        search_query = f"Find me {num_jobs} {job_title} jobs"
        if location:
            search_query += f" in {location}"
            
        print(f"\nSearching for: {search_query}")
        
        # Use the orchestrator to search and store jobs
        result = orchestrator(search_query)
        
        if result and isinstance(result, dict) and "jobs" in result:
            print(f"\nSuccessfully scraped {len(result['jobs'])} jobs!")
            print("Jobs have been stored in the database and embeddings have been created.")
        else:
            print("\nNo jobs found or an error occurred during the search.")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key in the .env file or as an environment variable.")
    else:
        main()
