# test_system.py
import os
from functions.orchestrator import orchestrator
from functions.scraper import scrape_jobs, save_jobs_to_json
from functions.embedder import embed_jobs
from functions.vector_store import build_faiss_index

def interactive_mode():
    print("Job Search System")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the program")
    print("Type 'help' to see available commands")
    print("=" * 50)
    
    while True:
        user_input = input("\nWhat would you like to search for? ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit']:
            print("\nExiting program. Goodbye!")
            break
            
        # Check for help command
        if user_input.lower() == 'help':
            print("\nAvailable commands:")
            print("- 'quit' or 'exit': End the program")
            print("- 'help': Show this help message")
            print("\nExample queries:")
            print("- Find me 5 data scientist jobs in New York")
            print("- Get me some software engineering jobs in Seattle")
            print("- Search for Python developer positions in Boston")
            continue
            
        # Process the search query
        result = orchestrator(user_input)
        
        # Check if result is a list (job results) or string (LLM response)
        if isinstance(result, list):
            # Save results to file
            save_jobs_to_json(result, "test_results.json")
            print(f"\nFound {len(result)} jobs. Results saved to test_results.json")
        else:
            # If result is a string (LLM response), just print it
            print("\nResponse:", result)

if __name__ == "__main__":
    # Make sure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OpenAI API key as an environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
    else:
        interactive_mode()
