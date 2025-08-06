import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import openai
import re
from company_generator import enrich_company_data
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json

# job_id SERIAL PRIMARY KEY,  
# "title": str,
#     "company": str,
#     "location": str,
#     "posting_date": datetime,
#     "description": str,
#     "yoe": int,
#     "education": list[str],
#     "employment_type": str,
#     "job_function": str,
#     "industry": str,
#     "salary": str,
#     source TEXT,                             -- e.g., 'Indeed', 'LinkedIn'
#     external_id TEXT,                        -- ID from source, if available
#     content_hash TEXT,                       -- For deduplication
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

# Given validated link, look for job cards or job links within the career page

def clean_html(html_content):
    """Remove unnecessary HTML to reduce token usage"""
    if not html_content:  # Add this check
        print("Warning: Empty HTML content received")
        return ""
        
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove unnecessary tags
        for tag in soup.find_all(["script", "style", "head", "footer", "img"]):
            tag.decompose()
        
        return str(soup)
    except Exception as e:
        print(f"Error cleaning HTML: {e}")
        return ""
    

def scrape_jobs_from_careers_page(careers_url):
    return None

def extract_job_metadata(content):
    """
    Use LLM to extract job fields from scraped content
    """
    return None

if __name__ == "__main__":
    # Test the scraper
    
    landing_contents = scrape_jobs_from_careers_page("https://careers.airbnb.com/positions/")
    clean_contents = clean_html(landing_contents['content'])
    with open('test.html', 'w', encoding='utf-8') as f:
            f.write(clean_contents)
    # if successfully access the site 
    if landing_contents['success']:
        print("Successfully scraped page")
   