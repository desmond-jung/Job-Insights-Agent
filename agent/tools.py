from langchain.tools import tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import get_all_jobs, search_jobs, get_job_by_id
from typing import Optional, List
from utils.email_service import email_service

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
        print(f"🔧 Tool called with: title='{title}', location='{location}', num_results={num_results}")
        jobs = db_search_jobs(title=title, location=location, num_jobs=num_results)
        print(f"🔧 Database returned {len(jobs)} jobs")
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

        print(f"🔧 Tool returning result with {len(jobs)} jobs")
        print(f"🔧 Result preview: {result[:200]}...")
        return result

    except Exception as e:
        print(f"🔧 Tool error: {str(e)}")
        return f"Error searching jobs: {str(e)}"
    

@tool
def get_job_statistics_tool(
    days_back: int = 7,
    title_filter: str = None
) -> str:
    """
    Get comprehensive statistics about jobs in the database
    
    Args:
        days_back: Number of days to look back for recent jobs (default: 7)
        title_filter: Filter statistics by job title (optional)

    Returns:
        Formatted string with job statistics
    """
    try:
        from data.database import get_job_statistics
        print(f"📊 Getting job statistics: days_back={days_back}, title_filter='{title_filter}'")
        stats = get_job_statistics(days_back=days_back, title_filter=title_filter)
        
        result = f"📊 Job Statistics (Last {days_back} days"
        if title_filter:
            result += f", filtered by '{title_filter}'"
        result += "):\n\n"
        
        result += f"📈 Total Jobs: {stats['total_jobs']}\n"
        result += f"🆕 Recent Jobs: {stats['recent_jobs']}\n"
        result += f"🏢 Top Companies: {', '.join(stats['top_companies'][:5])}\n"
        result += f"📍 Top Locations: {', '.join(stats['top_locations'][:5])}\n"
        result += f"💼 Remote Jobs: {stats['remote_jobs']} ({stats['remote_percentage']:.1f}%)\n"
        result += f"💰 Average Salary: ${stats['avg_salary']:,.0f}\n"
        result += f"📋 Employment Types: {', '.join(stats['employment_types'])}\n"
        
        return result
        
    except Exception as e:
        print(f"📊 Statistics tool error: {str(e)}")
        return f"Error getting job statistics: {str(e)}"


@tool
def send_job_results_email(
    recipient_email: str,
    job_ids: List[str],
    subject: str = "Job Search Results"
) -> str:
    """
    Send job search results to specified email address

    Args:
        recipient_email: Email address to send results to
        job_ids: List of job IDs to include in the email
        subject: Email subject line (optional)

    Returns:
        Confirmation message
    """
    try:
        # Get job details from database
        jobs = []
        for job_id in job_ids:
            job = get_job_by_id(job_id)
            if job:
                jobs.append(job)
        
        if not jobs:
            return "❌ No jobs found with the provided IDs"
        
        # Send email using the email service
        result = email_service.send_job_results_email(recipient_email, jobs, subject)
        return result['message']
        
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

@tool
def search_and_email_jobs(
    recipient_email: str,
    title: Optional[str] = None,
    location: Optional[str] = None,
    num_results: int = 5,
    subject: str = "Job Search Results"
) -> str:
    """
    Search for jobs and email results in one step
    
    Args:
        recipient_email: Email address to send results to
        title: Job title to search for
        location: Location to search in
        num_results: Number of jobs to include
        subject: Email subject line

    Returns:
        Confirmation message
    """
    try:
        # First search for jobs
        jobs = search_jobs(title=title, location=location, num_jobs=num_results)
        
        if not jobs:
            return f"❌ No jobs found matching '{title}' in {location}"
        
        # Send email using the email service
        result = email_service.send_job_results_email(recipient_email, jobs, subject)
        return result['message']
        
    except Exception as e:
        return f"❌ Error: {str(e)}"