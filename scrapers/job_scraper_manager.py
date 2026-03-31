"""
Job Scraper Manager - Centralized system for managing multiple job scraping sources
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import store_job
from scrapers.rss_scraper import RSSJobScraper
from scrapers.google_jobs_scraper import GoogleJobsScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraperManager:
    """
    Centralized manager for all job scraping operations
    """
    
    def __init__(self):
        self.scrapers = {
            'rss': RSSJobScraper(),
            'google': GoogleJobsScraper()
        }
        self.scraping_stats = {
            'total_jobs_scraped': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'last_scrape_time': None
        }
    
    def scrape_all_sources(self, 
                          rss_enabled: bool = True, 
                          google_enabled: bool = False,
                          max_jobs_per_source: int = 50) -> Dict:
        """
        Scrape jobs from all enabled sources
        
        Args:
            rss_enabled: Whether to scrape RSS feeds
            google_enabled: Whether to use Google Jobs API (requires API key)
            max_jobs_per_source: Maximum jobs to scrape per source
            
        Returns:
            Dictionary with scraping results and statistics
        """
        results = {
            'rss': {'jobs': [], 'error': None},
            'google': {'jobs': [], 'error': None},
            'summary': {
                'total_new_jobs': 0,
                'total_duplicates': 0,
                'scraping_time': None
            }
        }
        
        start_time = datetime.now()
        logger.info("🚀 Starting job scraping from all sources...")
        
        # Scrape RSS feeds
        if rss_enabled:
            logger.info("📡 Scraping RSS feeds...")
            try:
                rss_jobs = self.scrapers['rss'].scrape_jobs(max_jobs=max_jobs_per_source)
                results['rss']['jobs'] = rss_jobs
                logger.info(f"✅ RSS scraping completed: {len(rss_jobs)} jobs found")
            except Exception as e:
                results['rss']['error'] = str(e)
                logger.error(f"❌ RSS scraping failed: {e}")
        
        # Scrape Google Jobs (if API key is available)
        if google_enabled:
            logger.info("🔍 Scraping Google Jobs API...")
            try:
                google_jobs = self.scrapers['google'].scrape_jobs(max_jobs=max_jobs_per_source)
                results['google']['jobs'] = google_jobs
                logger.info(f"✅ Google Jobs scraping completed: {len(google_jobs)} jobs found")
            except Exception as e:
                results['google']['error'] = str(e)
                logger.error(f"❌ Google Jobs scraping failed: {e}")
        
        # Store all jobs in database
        all_jobs = results['rss']['jobs'] + results['google']['jobs']
        new_jobs, duplicates = self._store_jobs(all_jobs)
        
        # Update results
        results['summary']['total_new_jobs'] = new_jobs
        results['summary']['total_duplicates'] = duplicates
        results['summary']['scraping_time'] = (datetime.now() - start_time).total_seconds()
        
        # Update stats
        self.scraping_stats['total_jobs_scraped'] += len(all_jobs)
        self.scraping_stats['successful_scrapes'] += 1
        self.scraping_stats['last_scrape_time'] = datetime.now()
        
        logger.info(f"🎉 Scraping completed! {new_jobs} new jobs, {duplicates} duplicates")
        return results
    
    def _store_jobs(self, jobs: List[Dict]) -> tuple:
        """
        Store jobs in database and return count of new vs duplicate jobs
        
        Returns:
            Tuple of (new_jobs_count, duplicate_jobs_count)
        """
        new_jobs = 0
        duplicates = 0
        
        for job in jobs:
            try:
                # Try to store the job
                store_job(
                    job_id=job.get('id'),
                    job_url=job.get('url'),
                    source=job.get('source'),
                    title=job.get('title'),
                    company_name=job.get('company'),
                    description=job.get('description'),
                    location=job.get('location'),
                    city=job.get('city'),
                    state=job.get('state'),
                    country=job.get('country'),
                    remote=job.get('remote'),
                    industry=job.get('industry'),
                    seniority_level=job.get('seniority_level'),
                    employment_type=job.get('employment_type'),
                    job_function=job.get('job_function'),
                    salary_raw=job.get('salary_raw'),
                    salary_min=job.get('salary_min'),
                    salary_max=job.get('salary_max'),
                    salary_avg=job.get('salary_avg'),
                    yoe_raw=job.get('yoe_raw'),
                    yoe_min=job.get('yoe_min'),
                    yoe_max=job.get('yoe_max'),
                    yoe_avg=job.get('yoe_avg'),
                    education=job.get('education'),
                    skills=job.get('skills')
                )
                new_jobs += 1
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    duplicates += 1
                else:
                    logger.error(f"Error storing job {job.get('id', 'unknown')}: {e}")
        
        return new_jobs, duplicates
    
    def get_scraping_recommendations(self) -> Dict:
        """
        Get recommendations for job scraping strategies based on different use cases
        """
        return {
            'free_options': {
                'rss_feeds': {
                    'description': 'Scrape RSS feeds from job boards',
                    'pros': ['Free', 'Real-time', 'Easy to implement', 'No API limits'],
                    'cons': ['Limited data', 'Basic job info only', 'Inconsistent formatting'],
                    'best_for': 'Getting started, basic job aggregation',
                    'estimated_jobs_per_day': '100-500',
                    'implementation_difficulty': 'Easy'
                },
                'web_scraping': {
                    'description': 'Direct scraping of job board websites',
                    'pros': ['Free', 'Access to full job data', 'No API limits'],
                    'cons': ['Rate limiting', 'Anti-bot measures', 'Fragile (breaks when sites change)', 'Legal concerns'],
                    'best_for': 'Specific job boards, when APIs are not available',
                    'estimated_jobs_per_day': '200-1000',
                    'implementation_difficulty': 'Hard'
                }
            },
            'paid_options': {
                'google_jobs_api': {
                    'description': 'Google Custom Search API for job postings',
                    'cost': '$5 per 1,000 queries',
                    'pros': ['High-quality data', 'Aggregates multiple sources', 'Rich job descriptions', 'Reliable'],
                    'cons': ['Costs money', 'Query limits', 'Requires API key'],
                    'best_for': 'High-quality job data, professional job boards',
                    'estimated_jobs_per_day': '1,000-5,000',
                    'implementation_difficulty': 'Medium'
                },
                'indeed_api': {
                    'description': 'Indeed Partner API',
                    'cost': '$0.10 per job posting',
                    'pros': ['Millions of jobs', 'Global coverage', 'Detailed job data', 'Official API'],
                    'cons': ['Costs money', 'Requires approval', 'Complex setup'],
                    'best_for': 'Large-scale job aggregation, commercial use',
                    'estimated_jobs_per_day': '10,000+',
                    'implementation_difficulty': 'Hard'
                },
                'adzuna_api': {
                    'description': 'Adzuna Job Market API',
                    'cost': '$0.05 per job posting',
                    'pros': ['Salary data', 'Company insights', 'Global coverage', 'Good documentation'],
                    'cons': ['Costs money', 'Limited to certain regions', 'API rate limits'],
                    'best_for': 'Salary-focused job boards, market analysis',
                    'estimated_jobs_per_day': '5,000-20,000',
                    'implementation_difficulty': 'Medium'
                }
            },
            'recommendations': {
                'start_small': {
                    'strategy': 'Begin with RSS feeds',
                    'reason': 'Free, easy to implement, good for testing',
                    'next_step': 'Add Google Jobs API when ready to scale'
                },
                'scale_up': {
                    'strategy': 'Combine RSS + Google Jobs API',
                    'reason': 'Balances cost and data quality',
                    'next_step': 'Add Indeed API for maximum coverage'
                },
                'enterprise': {
                    'strategy': 'Multiple APIs + custom scraping',
                    'reason': 'Maximum job coverage and data quality',
                    'next_step': 'Implement job deduplication and quality scoring'
                }
            }
        }
    
    def get_scraping_schedule_recommendations(self) -> Dict:
        """
        Get recommendations for how often to scrape different sources
        """
        return {
            'rss_feeds': {
                'frequency': 'Every 15-30 minutes',
                'reason': 'RSS feeds update frequently, real-time data is valuable',
                'best_times': ['9 AM', '12 PM', '3 PM', '6 PM'],
                'weekend_scraping': 'Yes, but less frequent'
            },
            'google_jobs_api': {
                'frequency': 'Every 2-4 hours',
                'reason': 'API costs money, balance freshness with cost',
                'best_times': ['8 AM', '12 PM', '4 PM', '8 PM'],
                'weekend_scraping': 'Yes, but reduced frequency'
            },
            'indeed_api': {
                'frequency': 'Every 6-12 hours',
                'reason': 'High volume, expensive, focus on peak hiring times',
                'best_times': ['9 AM', '3 PM'],
                'weekend_scraping': 'No, focus on weekdays'
            },
            'adzuna_api': {
                'frequency': 'Every 4-8 hours',
                'reason': 'Good balance of freshness and cost',
                'best_times': ['10 AM', '2 PM', '6 PM'],
                'weekend_scraping': 'Yes, but less frequent'
            }
        }

def main():
    """
    Main function to run job scraping
    """
    manager = JobScraperManager()
    
    print("🎯 Job Scraper Manager")
    print("=" * 50)
    
    # Show recommendations
    recommendations = manager.get_scraping_recommendations()
    print("\n📋 Scraping Strategy Recommendations:")
    print("-" * 40)
    
    for category, options in recommendations.items():
        if category == 'recommendations':
            continue
        print(f"\n{category.upper()}:")
        for name, details in options.items():
            print(f"  • {name.replace('_', ' ').title()}: {details['description']}")
            if 'cost' in details:
                print(f"    Cost: {details['cost']}")
            print(f"    Best for: {details['best_for']}")
    
    print("\n🚀 Starting job scraping...")
    
    # Run scraping (RSS only for now, since Google API requires setup)
    results = manager.scrape_all_sources(
        rss_enabled=True,
        google_enabled=False,  # Set to True when you have Google API key
        max_jobs_per_source=25
    )
    
    # Print results
    print(f"\n📊 Scraping Results:")
    print(f"  • New jobs added: {results['summary']['total_new_jobs']}")
    print(f"  • Duplicates skipped: {results['summary']['total_duplicates']}")
    print(f"  • Scraping time: {results['summary']['scraping_time']:.2f} seconds")
    
    if results['rss']['error']:
        print(f"  • RSS errors: {results['rss']['error']}")
    
    if results['google']['error']:
        print(f"  • Google errors: {results['google']['error']}")

if __name__ == "__main__":
    main()
