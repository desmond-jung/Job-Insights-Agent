import requests
import time
from bs4 import BeautifulSoup
import re
import json

def clean_description(description):
    if description:
        description = description.text
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', description)
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

def scrape_jobs(num_jobs: int = 50) -> list:
    all_jobs = []
    jobs_found = 0

    # 1. Scrape job listing pages
    start_position = 0
    while jobs_found < num_jobs:
        list_url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?f_TPR=r2592000&start={start_position}"  # r2592000 filters for jobs posted in last 30 days
        )
        response = requests.get(list_url)
        if response.status_code == 200:
            list_data = response.text
            list_soup = BeautifulSoup(list_data, "html.parser")
            more_jobs = list_soup.find_all("li")
            
            # Only add jobs up to the requested number
            remaining_jobs = num_jobs - jobs_found
            jobs_to_add = more_jobs[:remaining_jobs]
            all_jobs.extend(jobs_to_add)
            jobs_found += len(jobs_to_add)
            
            print(f"Found {len(jobs_to_add)} jobs on page {start_position//10 + 1}")
            
            if len(more_jobs) < 10:  # If we got fewer than 10 jobs, we've reached the end
                break
                
            start_position += 10
        else:
            print(f"Failed to fetch page {start_position//10 + 1}")
            break

    # 2. Extract job IDs
    job_id_list = []
    for job in all_jobs:
        base_card_div = job.find("div", {"class": "base-card"})
        if base_card_div:
            job_id = base_card_div.get("data-entity-urn", "")
            if job_id:
                job_id = job_id.split(":")[3]
                job_id_list.append(job_id)
    job_id_list = set(job_id_list)
    print(f"Found {len(job_id_list)} unique job IDs")

    # 3. Scrape each job posting
    job_list = []
    for job_id in job_id_list:
        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        job_response = requests.get(job_url)
        if job_response.status_code == 429:
            time.sleep(5)
            job_response = requests.get(job_url)
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        job_post = {}

        # Clean description
        raw_description = job_soup.find("div", {"class": "description__text description__text--rich"})
        cleaned_desc = clean_description(raw_description)

        job_post["id"] = job_id
        job_post["title"] = job_soup.find("h2", {"class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip() if job_soup.find("h2", {"class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}) else None
        job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip() if job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}) else None
        job_post["location"] = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip() if job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}) else None
        job_post["description"] = cleaned_desc

        # Industries
        try:
            level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
            emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            job_header = emp_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            industry_header = job_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            industry = industry_header.find_next_sibling("span").text.strip()
            job_post["industry"] = industry
        except:
            job_post["industry"] = "Industry not specified"

        job_list.append(job_post)

    return job_list

# Optional: test block
if __name__ == "__main__":
    jobs = scrape_jobs(num_jobs=5)
    print(f"Scraped {len(jobs)} jobs")
    print(json.dumps(jobs[0], indent=2))

    
   