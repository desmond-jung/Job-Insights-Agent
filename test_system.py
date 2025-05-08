# test_system.py
import os
from functions.orchestrator import orchestrator
from functions.scraper import scrape_jobs, save_jobs_to_json
from functions.embedder import embed_jobs
from functions.vector_store import build_faiss_index

def test_system():
    print("Job Search System Test")
    print("=" * 50)
    
    # Test 1: Basic job scraping
    print("\nTest 1: Basic Job Scraping")
    print("-" * 30)
    test_query = "Find me 3 machine learning jobs in San Francisco"
    print(f"Query: {test_query}")
    result = orchestrator(test_query)
    
    if result:
        print("\nSuccessfully scraped jobs!")
        # Save the results to a JSON file
        save_jobs_to_json(result, "test_results.json")
        print("Results saved to test_results.json")
    else:
        print("Failed to scrape jobs")

    # Test 2: Interactive mode
    print("\nTest 2: Interactive Mode")
    print("-" * 30)
    print("Enter 'quit' to exit")
    
    while True:
        user_input = input("\nWhat would you like to search for? ")
        if user_input.lower() == 'quit':
            break
            
        result = orchestrator(user_input)
        if result:
            print("\nResults:")
            print("-" * 20)
            for job in result:
                print(f"\nTitle: {job.get('title', 'N/A')}")
                print(f"Company: {job.get('company_name', 'N/A')}")
                print(f"Location: {job.get('location', 'N/A')}")
                print(f"Employment Type: {job.get('employment_type', 'N/A')}")
                print("-" * 20)

if __name__ == "__main__":
    # Make sure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OpenAI API key as an environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
    else:
        test_system()
