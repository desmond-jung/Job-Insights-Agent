"""
Google Jobs Scraper - Scrapes job postings using Google Custom Search API
"""

import os
import requests
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GoogleJobsScraper:
    """
    Scraper for job postings using Google Custom Search API
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.base_url = 'https://www.googleapis.com/customsearch/v1'
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google API credentials not found. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """
        Scrape jobs using Google Custom Search API
        
        Args:
            max_jobs: Maximum number of jobs to scrape
            
        Returns:
            List of job dictionaries
        """
        if not self.api_key or not self.search_engine_id:
            logger.error("Google API credentials not configured")
            return []
        
        jobs = []
        search_queries = [
            'software engineer jobs',
            'data scientist jobs',
            'product manager jobs',
            'marketing jobs',
            'sales jobs'
        ]
        
        jobs_per_query = max_jobs // len(search_queries)
        
        for query in search_queries:
            try:
                logger.info(f"Searching Google for: {query}")
                query_jobs = self._search_jobs(query, jobs_per_query)
                jobs.extend(query_jobs)
            except Exception as e:
                logger.error(f"Error searching for {query}: {e}")
                continue
        
        return jobs[:max_jobs]
    
    def _search_jobs(self, query: str, max_results: int) -> List[Dict]:
        """
        Search for jobs using Google Custom Search API
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(max_results, 10),  # Google API limit
                'siteSearch': 'linkedin.com OR indeed.com OR glassdoor.com OR monster.com'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    job = self._parse_google_result(item)
                    if job:
                        jobs.append(job)
            
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
        
        return jobs
    
    def _parse_google_result(self, item: Dict) -> Optional[Dict]:
        """
        Parse Google search result into job dictionary
        
        Args:
            item: Google search result item
            
        Returns:
            Job dictionary or None if parsing fails
        """
        try:
            title = item.get('title', '').strip()
            link = item.get('link', '')
            snippet = item.get('snippet', '')
            
            if not title or not link:
                return None
            
            # Generate unique job ID
            job_id = hashlib.md5(f"google_{title}_{link}".encode()).hexdigest()
            
            # Extract company name from title
            company = self._extract_company_from_title(title)
            
            # Extract location from title or snippet
            location = self._extract_location_from_text(f"{title} {snippet}")
            
            job = {
                'id': job_id,
                'url': link,
                'source': 'google.com',
                'title': title,
                'company': company,
                'description': snippet,
                'location': location,
                'city': self._extract_city(location),
                'state': self._extract_state(location),
                'country': self._extract_country(location),
                'remote': '1' if 'remote' in location.lower() or 'remote' in snippet.lower() else '0',
                'industry': None,
                'seniority_level': self._extract_seniority_level(snippet),
                'employment_type': self._extract_employment_type(snippet),
                'job_function': None,
                'salary_raw': None,
                'salary_min': None,
                'salary_max': None,
                'salary_avg': None,
                'yoe_raw': None,
                'yoe_min': None,
                'yoe_max': None,
                'yoe_avg': None,
                'education': [],
                'skills': [],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return job
            
        except Exception as e:
            logger.error(f"Error parsing Google result: {e}")
            return None
    
    def _extract_company_from_title(self, title: str) -> str:
        """Extract company name from job title"""
        # Common patterns for company names in job titles
        import re
        
        patterns = [
            r'at\s+([A-Z][a-zA-Z\s&]+?)(?:\s*[-–]\s|$)',
            r'-\s*([A-Z][a-zA-Z\s&]+?)(?:\s*[-–]\s|$)',
            r'@\s*([A-Z][a-zA-Z\s&]+?)(?:\s*[-–]\s|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 2 and len(company) < 50:
                    return company
        
        # Fallback: try to extract from title
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) > 1:
                return parts[-1].strip()
        
        return 'Unknown Company'
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from text"""
        import re
        
        # Common location patterns
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)',
            r'(Remote|Work from home|WFH)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1:
                    return f"{match.group(1)}, {match.group(2)}"
                else:
                    location = match.group(1)
                    if len(location) > 2 and len(location) < 50:
                        return location
        
        return 'Location not specified'
    
    def _extract_city(self, location: str) -> str:
        """Extract city from location string"""
        if ',' in location:
            return location.split(',')[0].strip()
        return location
    
    def _extract_state(self, location: str) -> str:
        """Extract state from location string"""
        if ',' in location:
            parts = location.split(',')
            if len(parts) > 1:
                return parts[1].strip()
        return ''
    
    def _extract_country(self, location: str) -> str:
        """Extract country from location string"""
        if 'remote' in location.lower():
            return 'Remote'
        elif 'united states' in location.lower() or 'usa' in location.lower():
            return 'United States'
        elif ',' in location:
            parts = location.split(',')
            if len(parts) > 2:
                return parts[2].strip()
        return 'United States'  # Default assumption
    
    def _extract_employment_type(self, text: str) -> str:
        """Extract employment type from text"""
        text_lower = text.lower()
        
        if 'full-time' in text_lower or 'full time' in text_lower:
            return 'Full-time'
        elif 'part-time' in text_lower or 'part time' in text_lower:
            return 'Part-time'
        elif 'contract' in text_lower:
            return 'Contract'
        elif 'intern' in text_lower:
            return 'Internship'
        else:
            return 'Full-time'  # Default assumption
    
    def _extract_seniority_level(self, text: str) -> str:
        """Extract seniority level from text"""
        text_lower = text.lower()
        
        if 'senior' in text_lower or 'sr.' in text_lower:
            return 'Senior'
        elif 'junior' in text_lower or 'jr.' in text_lower:
            return 'Junior'
        elif 'lead' in text_lower or 'principal' in text_lower:
            return 'Lead'
        elif 'manager' in text_lower or 'director' in text_lower:
            return 'Management'
        elif 'intern' in text_lower or 'internship' in text_lower:
            return 'Intern'
        else:
            return 'Mid-level'  # Default assumption

def test_google_scraper():
    """Test function for Google Jobs scraper"""
    scraper = GoogleJobsScraper()
    
    if not scraper.api_key or not scraper.search_engine_id:
        print("❌ Google API credentials not configured")
        print("Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables")
        return
    
    jobs = scraper.scrape_jobs(max_jobs=5)
    
    print(f"Found {len(jobs)} jobs:")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")
        print()

if __name__ == "__main__":
    test_google_scraper()
