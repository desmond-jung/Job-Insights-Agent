import openai
import os
import json
from functions.scraper import scrape_jobs, save_jobs_to_json
from functions.database import init_db, store_jobs, get_job_by_id
from functions.embedder import embed_jobs
from functions.vector_store import build_faiss_index

client = openai.api_key = os.getenv("OPENAI_API_KEY")


functions = [
    {
        "name": "scrape_jobs",
        "description": "Scrape job postings for a given title and location.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Job title to search for"},
                "location": {"type": "string", "description": "Location to search in"},
                "num_jobs": {"type": "integer", "description": "Number of jobs to fetch"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "save_jobs_to_json",
        "description": "Save job postings to a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_list": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "company_name": {"type": "string"},
                            "location": {"type": "string"},
                            "description": {"type": "string"},
                            "seniority_level": {"type": "string"},
                            "employment_type": {"type": "string"},
                            "job_function": {"type": "string"},
                            "industry": {"type": "string"},
                            "yoe": {"type": "array", "items": {"type": "string"}},
                            "education": {"type": "array", "items": {"type": "string"}},
                            "salary": {"type": "string"}
                        }
                    },
                    "description": "List of job dictionaries"
                },
                "filename": {"type": "string", "description": "Output JSON filename"}
            },
            "required": ["job_list"]
        }
    },
    {
        "name": "embed_jobs",
        "description": "Generate embeddings for job descriptions.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_descriptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of job descriptions"
                },
                "method": {"type": "string", "description": "Embedding method (sbert or openai)"}
            },
            "required": ["job_descriptions"]
        }
    },
    {
        "name": "build_faiss_index",
        "description": "Build a FAISS index from job embeddings.",
        "parameters": {
            "type": "object",
            "properties": {
                "embeddings": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "List of embeddings"
                },
                "index_path": {"type": "string", "description": "Path to save the index"}
            },
            "required": ["embeddings"]
        }
    }
]

def call_function_by_name(name, arguments):
    try:
        if name == "scrape_jobs":
            return scrape_jobs(**arguments)
        elif name == "save_jobs_to_json":
            return save_jobs_to_json(**arguments)
        elif name == "embed_jobs":
            return embed_jobs(**arguments)
        elif name == "build_faiss_index":
            return build_faiss_index(**arguments)
        else:
            raise ValueError(f"Unknown function: {name}")
    except Exception as e:
        print(f"Error calling {name}: {str(e)}")
        return None

def orchestrator(user_prompt):
    try:
        messages = [
            {"role": "system", "content": "You are a job search assistant that helps users find and analyze job postings."},
            {"role": "user", "content": user_prompt}
        ]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=[{"type": "function", "function": func} for func in functions],
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                result = call_function_by_name(func_name, arguments)
                return result
        else:
            return message.content
            
    except Exception as e:
        print(f"Error in orchestrator: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the orchestrator
    test_queries = [
        "Find me 5 machine learning jobs in San Francisco",
        "Scrape 10 data scientist positions in New York",
        "Get me some software engineering jobs in Seattle"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        print("-" * 50)
        orchestrator(query)
        print("-" * 50) 