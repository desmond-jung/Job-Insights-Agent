from langchain.tools import tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import get_all_jobs, search_jobs
from typing import Optional

@tool
def search_jobs_tool(
    title: Optional[str] = None,
    location: Optional[str] = None,
    num_results: int = 2
) -> str:
    """
    Search for jobs in the database by title and location. If not specified, search for most relevant jobs
    
    Args:
        title: Job title to search for (e.g., software engineer)
        location: Location to search in (e.g., San Francisco)
        num_results: Number of jobs to return (default:2)

    Returns:
        Formatted string with job search results
    """

    try:
        from data.database import search_jobs as db_search_jobs
        jobs = db_search_jobs(title=title, location=location, num_jobs=num_results)
        if not jobs:
            return f"No jobs found matching your criteria"
        
        result = f"Found {len(jobs)} jobs:\n\n"
        for i, job in enumerate(jobs, 1):
            result += f"{i}. {job.get('title', 'N/A')}\n"
            result += f"   Company: {job.get('company_name', 'N/A')}\n"
            result += f"   Location: {job.get('location', 'N/A')}\n"
            result += f"   Type: {job.get('employment_type', 'N/A')}\n"
            result += f"   Experience: {job.get('yoe_raw', 'N/A')} years\n"
            result += f"   Description: {job.get('description', 'N/A')[:200]}...\n"
            result += "-" * 50 + "\n"

    except Exception as e:
        return f"Error searching jobs: {str(e)}"