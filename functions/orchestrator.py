import json
from openai import OpenAI
from functions.scraper import scrape_jobs
from functions.database import init_db, store_jobs, get_job_by_id
from functions.embedder import embed_jobs
from functions.vector_store import build_faiss_index
from functions.skill_extractor import extract_skills
from dotenv import load_dotenv
from functions.email_sender import send_email
import os

load_dotenv()

init_db()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


functions = [
    {
        "name": "scrape_jobs",
        "description": "Scrape job postings from LinkedIn",
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
        "name": "get_job_by_id",
        "description": "Get details of a specific job by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "The ID of the job to retrieve"
                }
            },
            "required": ["job_id"]
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
    },
    {
        "name": "send_email",
        "description": "Send job search results via email",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient_email": {
                    "type": "string",
                    "description": "Email address to send results to"
                }
            },
            "required": ["recipient_email"]
        }
    },
    {
        "name": "extract_skills",
        "description": "Extract key skills for specified job title",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Job title to extract skills for"},
                "location": {"type": "string", "description": "Location to search in"},
                "num_jobs": {"type": "integer", "description": "Number of jobs to fetch"}
            },
            "required": ["job_title"]
        }
    }
]

def call_function_by_name(name, arguments):
    try:
        if name == "scrape_jobs":
            # First scrape the jobs
            jobs = scrape_jobs(**arguments)
            # Then store them in the database
            store_jobs(jobs)
            return jobs
        elif name == "embed_jobs":
            return embed_jobs(**arguments)
        elif name == "build_faiss_index":
            return build_faiss_index(**arguments)
        elif name == "get_job_by_id":
            return get_job_by_id(**arguments)
        elif name == "extract_skills":
            jobs = scrape_jobs(**arguments)
            descriptions = [job['description'] for job in jobs if job.get('description')]
            return extract_skills(" ".join(descriptions))
        elif name == "send_email":
            return send_email(**arguments)
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
                
                # If the function called was scrape_jobs, automatically process the results
                if func_name == "scrape_jobs" and result:
                    # Store jobs in database
                    
                    # Generate embeddings for job descriptions
                    descriptions = [job['description'] for job in result] # for each result in outputted dict, grab desc
                    embeddings = embed_jobs(job_descriptions=descriptions)

                    # Build index
                    faiss_index = build_faiss_index(embeddings=embeddings)

                    result = {
                        "jobs": result,
                        "message": f"Found {len(result)} jobs. Stored in database and created embeddings"
                    }
                return result
        else:
            return message.content
            
    except Exception as e:
        print(f"Error in orchestrator: {str(e)}")
        return None

if __name__ == "__main__":
    print("HI")