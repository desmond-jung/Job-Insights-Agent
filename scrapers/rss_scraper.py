"""
RSS Job Scraper - Scrapes job postings from RSS feeds
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RSSJobScraper:
    """
    Scraper for job postings from RSS feeds
    """
    
    def __init__(self):
        self.rss_feeds = [
            {
                'name': 'LinkedIn Jobs',
                'url': 'https://www.linkedin.com/jobs/search/rss/?keywords=software%20engineer&location=United%20States',
                'source': 'linkedin.com'
            },
            {
                'name': 'Indeed Jobs',
                'url': 'https://rss.indeed.com/rss?q=software+engineer&l=United+States',
                'source': 'indeed.com'
            },
            {
                'name': 'Remote Jobs',
                'url': 'https://remote.co/remote-jobs/feed/',
                'source': 'remote.co'
            },
            {
                'name': 'AngelList Jobs',
                'url': 'https://angel.co/jobs.rss',
                'source': 'angel.co'
            }
        ]
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """
        Scrape jobs from RSS feeds
        
        Args:
            max_jobs: Maximum number of jobs to scrape
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        for feed in self.rss_feeds:
            try:
                logger.info(f"Scraping RSS feed: {feed['name']}")
                jobs = self._scrape_feed(feed, max_jobs // len(self.rss_feeds))
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs from {feed['name']}")
            except Exception as e:
                logger.error(f"Error scraping {feed['name']}: {e}")
                continue
        
        # Remove duplicates and limit results
        unique_jobs = self._remove_duplicates(all_jobs)
        return unique_jobs[:max_jobs]
    
    def _scrape_feed(self, feed: Dict, max_jobs: int) -> List[Dict]:
        """
        Scrape jobs from a single RSS feed
        
        Args:
            feed: Feed configuration dictionary
            max_jobs: Maximum jobs to scrape from this feed
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # Parse RSS feed
            feed_data = feedparser.parse(feed['url'])
            
            if feed_data.bozo:
                logger.warning(f"RSS feed {feed['name']} has parsing issues")
            
            for entry in feed_data.entries[:max_jobs]:
                try:
                    job = self._parse_rss_entry(entry, feed['source'])
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing RSS entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed['name']}: {e}")
        
        return jobs
    
    def _parse_rss_entry(self, entry, source: str) -> Optional[Dict]:
        """
        Parse a single RSS entry into a job dictionary
        
        Args:
            entry: RSS entry object
            source: Source website name
            
        Returns:
            Job dictionary or None if parsing fails
        """
        try:
            # Extract basic information
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            description = entry.get('description', '')
            published = entry.get('published', '')
            
            if not title or not link:
                return None
            
            # Generate unique job ID
            job_id = hashlib.md5(f"{source}_{title}_{link}".encode()).hexdigest()
            
            # Extract company name from title or description
            company = self._extract_company(title, description)
            
            # Extract location
            location = self._extract_location(title, description)
            
            # Extract salary information
            salary_info = self._extract_salary(description)
            
            # Extract employment type
            employment_type = self._extract_employment_type(description)
            
            # Parse published date
            published_date = self._parse_date(published)
            
            job = {
                'id': job_id,
                'url': link,
                'source': source,
                'title': title,
                'company': company,
                'description': description,
                'location': location,
                'city': self._extract_city(location),
                'state': self._extract_state(location),
                'country': self._extract_country(location),
                'remote': '1' if 'remote' in location.lower() or 'remote' in description.lower() else '0',
                'industry': None,
                'seniority_level': self._extract_seniority_level(description),
                'employment_type': employment_type,
                'job_function': None,
                'salary_raw': salary_info.get('raw'),
                'salary_min': salary_info.get('min'),
                'salary_max': salary_info.get('max'),
                'salary_avg': salary_info.get('avg'),
                'yoe_raw': None,
                'yoe_min': None,
                'yoe_max': None,
                'yoe_avg': None,
                'education': [],
                'skills': [],
                'created_at': published_date
            }
            
            return job
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    def _extract_company(self, title: str, description: str) -> str:
        """Extract company name from title or description"""
        # Common patterns for company names in job titles
        patterns = [
            r'at\s+([A-Z][a-zA-Z\s&]+?)(?:\s*[-–]\s|$)',
            r'-\s*([A-Z][a-zA-Z\s&]+?)(?:\s*[-–]\s|$)',
            r'@\s*([A-Z][a-zA-Z\s&]+?)(?:\s*[-–]\s|$)',
        ]
        
        text = f"{title} {description}"
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
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
    
    def _extract_location(self, title: str, description: str) -> str:
        """Extract location from title or description"""
        # Common location patterns
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)',
            r'(Remote|Work from home|WFH)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        text = f"{title} {description}"
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
    
    def _extract_salary(self, description: str) -> Dict:
        """Extract salary information from description"""
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[-–]\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*\+',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[-–]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*k',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    min_sal = int(match.group(1).replace(',', ''))
                    max_sal = int(match.group(2).replace(',', ''))
                    return {
                        'raw': match.group(0),
                        'min': min_sal,
                        'max': max_sal,
                        'avg': (min_sal + max_sal) / 2
                    }
                else:
                    sal = int(match.group(1).replace(',', ''))
                    return {
                        'raw': match.group(0),
                        'min': sal,
                        'max': None,
                        'avg': sal
                    }
        
        return {'raw': None, 'min': None, 'max': None, 'avg': None}
    
    def _extract_employment_type(self, description: str) -> str:
        """Extract employment type from description"""
        description_lower = description.lower()
        
        if 'full-time' in description_lower or 'full time' in description_lower:
            return 'Full-time'
        elif 'part-time' in description_lower or 'part time' in description_lower:
            return 'Part-time'
        elif 'contract' in description_lower:
            return 'Contract'
        elif 'intern' in description_lower:
            return 'Internship'
        else:
            return 'Full-time'  # Default assumption
    
    def _extract_seniority_level(self, description: str) -> str:
        """Extract seniority level from description"""
        description_lower = description.lower()
        
        if 'senior' in description_lower or 'sr.' in description_lower:
            return 'Senior'
        elif 'junior' in description_lower or 'jr.' in description_lower:
            return 'Junior'
        elif 'lead' in description_lower or 'principal' in description_lower:
            return 'Lead'
        elif 'manager' in description_lower or 'director' in description_lower:
            return 'Management'
        elif 'intern' in description_lower or 'internship' in description_lower:
            return 'Intern'
        else:
            return 'Mid-level'  # Default assumption
    
    def _parse_date(self, date_string: str) -> str:
        """Parse date string to standard format"""
        try:
            if not date_string:
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Try to parse the date
            from dateutil import parser
            parsed_date = parser.parse(date_string)
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs

def test_rss_scraper():
    """Test function for RSS scraper"""
    scraper = RSSJobScraper()
    jobs = scraper.scrape_jobs(max_jobs=5)
    
    print(f"Found {len(jobs)} jobs:")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")
        print()

if __name__ == "__main__":
    test_rss_scraper()
