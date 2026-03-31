#!/usr/bin/env python3
"""
Simple script to run job scraping for your job board
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.job_scraper_manager import JobScraperManager

def main():
    print("🎯 Job Board Scraper")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the scraper manager
    manager = JobScraperManager()
    
    # Show current recommendations
    print("📋 Current Scraping Strategy:")
    print("  • RSS Feeds: ENABLED (Free, real-time)")
    print("  • Google Jobs API: DISABLED (Requires API key setup)")
    print("  • Indeed API: DISABLED (Requires API key setup)")
    print("  • Adzuna API: DISABLED (Requires API key setup)")
    print()
    
    # Ask user what they want to do
    print("What would you like to do?")
    print("1. Scrape jobs now (RSS feeds only)")
    print("2. Show scraping recommendations")
    print("3. Show scraping schedule recommendations")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting job scraping...")
        print("This will scrape RSS feeds for new job postings.")
        print()
        
        # Run scraping
        results = manager.scrape_all_sources(
            rss_enabled=True,
            google_enabled=False,
            max_jobs_per_source=50
        )
        
        # Show results
        print("\n📊 Scraping Results:")
        print("-" * 30)
        print(f"✅ New jobs added: {results['summary']['total_new_jobs']}")
        print(f"⏭️  Duplicates skipped: {results['summary']['total_duplicates']}")
        print(f"⏱️  Scraping time: {results['summary']['scraping_time']:.2f} seconds")
        
        if results['rss']['error']:
            print(f"❌ RSS errors: {results['rss']['error']}")
        
        print(f"\n🎉 Scraping completed! Your job board now has more jobs.")
        print("Visit http://127.0.0.1:8080 to see the updated job board.")
        
    elif choice == "2":
        print("\n📋 Job Scraping Recommendations:")
        print("=" * 50)
        
        recommendations = manager.get_scraping_recommendations()
        
        print("\n🆓 FREE OPTIONS:")
        for name, details in recommendations['free_options'].items():
            print(f"\n• {name.replace('_', ' ').title()}:")
            print(f"  Description: {details['description']}")
            print(f"  Best for: {details['best_for']}")
            print(f"  Jobs per day: {details['estimated_jobs_per_day']}")
            print(f"  Difficulty: {details['implementation_difficulty']}")
            print(f"  Pros: {', '.join(details['pros'])}")
            print(f"  Cons: {', '.join(details['cons'])}")
        
        print("\n💰 PAID OPTIONS:")
        for name, details in recommendations['paid_options'].items():
            print(f"\n• {name.replace('_', ' ').title()}:")
            print(f"  Description: {details['description']}")
            print(f"  Cost: {details['cost']}")
            print(f"  Best for: {details['best_for']}")
            print(f"  Jobs per day: {details['estimated_jobs_per_day']}")
            print(f"  Difficulty: {details['implementation_difficulty']}")
            print(f"  Pros: {', '.join(details['pros'])}")
            print(f"  Cons: {', '.join(details['cons'])}")
        
        print("\n🎯 RECOMMENDED STRATEGIES:")
        for name, strategy in recommendations['recommendations'].items():
            print(f"\n• {name.replace('_', ' ').title()}:")
            print(f"  Strategy: {strategy['strategy']}")
            print(f"  Reason: {strategy['reason']}")
            print(f"  Next step: {strategy['next_step']}")
        
    elif choice == "3":
        print("\n⏰ Scraping Schedule Recommendations:")
        print("=" * 50)
        
        schedule = manager.get_scraping_schedule_recommendations()
        
        for source, details in schedule.items():
            print(f"\n• {source.replace('_', ' ').title()}:")
            print(f"  Frequency: {details['frequency']}")
            print(f"  Reason: {details['reason']}")
            print(f"  Best times: {', '.join(details['best_times'])}")
            print(f"  Weekend scraping: {details['weekend_scraping']}")
        
    elif choice == "4":
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
