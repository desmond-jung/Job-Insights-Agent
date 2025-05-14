# test_system.py
import os
from functions.orchestrator import orchestrator
from functions.scraper import scrape_jobs
from functions.embedder import embed_jobs
from functions.vector_store import build_faiss_index
from functions.database import list_all_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("\nJob Search Assistant")
    print("=" * 50)
    print("I can help you search for jobs and send results via email.")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    # Keep track of conversation context
    context = {
        "last_search": None,
        "jobs_found": False
    }
    
    while True:
        user_input = input("\nHow can I help you? ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break
            
        # Process the user's request
        result = orchestrator(user_input)
        
        # Update context based on the result
        if result and isinstance(result, dict) and "jobs" in result:
            context["last_search"] = result
            context["jobs_found"] = True
            print(f"\n{result['message']}")
            
            # Follow-up question
            print("\nWould you like me to:")
            print("1. Search for more jobs")
            print("2. Send these results via email")
            print("3. View the jobs in the database")
            
        elif "email" in user_input.lower():
            if not context["jobs_found"]:
                print("\nI haven't found any jobs yet. Would you like to search for some?")
            else:
                email = input("\nPlease enter your email address: ").strip()
                try:
                    send_result = orchestrator(f"Send the job results to {email}")
                    print("\nEmail sent successfully!")
                except Exception as e:
                    print(f"\nError sending email: {str(e)}")
        
        else:
            print("\n" + str(result))

def test_skill_extraction():
    print("\nTesting skill extraction for 'Data Scientist'...")
    result = orchestrator("What are the main skills for a Data Scientist in New York?")
    print("Extracted skills:", result)

if __name__ == "__main__":
    jobs = list_all_jobs()
    print(f"Total jobs in database: {len(jobs)}\n")
    for i, job in enumerate(jobs, 1):
        print(f"Job #{i}")
        for k, v in job.items():
            print(f"  {k}: {v}")
        print("-" * 40)
        if i >= 10:
            print("... (showing first 10 jobs only)")
            break 
    