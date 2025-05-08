import requests
import time
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import random
import urllib.parse
import json
from sentence_transformers import SentenceTransformer
import faiss

def clean_description(description):
    if description:
        description = description.text
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', description)
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

def scrape_jobs(title: str, location: str = "", num_jobs: int = 50) -> list:
    encoded_job_title = title.replace(" ", "%2B")
    encoded_location = location.replace(" ", "%2B")
    all_jobs = []

    # 1. Scrape job listing pages
    for start_position in range(0, num_jobs + 1, 10):
        list_url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={encoded_job_title}&location={encoded_location}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&start={start_position}"
        )
        response = requests.get(list_url)
        if response.status_code == 200:
            list_data = response.text
            list_soup = BeautifulSoup(list_data, "html.parser")
            more_jobs = list_soup.find_all("li")
            all_jobs.extend(more_jobs)
            print(f"Found {len(more_jobs)} jobs on page {start_position//10 + 1}")  # Debug print
        else:
            print(f"Failed to fetch page {start_position//10 + 1}")  # Debug print
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
    print(f"Found {len(job_id_list)} unique job IDs")  # Debug print

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

        # Seniority Level
        try:
            level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
            sen_level = level_header.find_next_sibling("span").text.strip()
        except AttributeError:
            sen_level = None
        job_post["seniority_level"] = sen_level

        # Employment Type (Fulltime, Part-time, internship)
        try:
            level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
            emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            emp_type = emp_header.find_next_sibling("span").text.strip()
            job_post["employment_type"] = emp_type
            
        except:
            job_post["employment_type"] = None

        # Job Function
        try:
            level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
            emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            job_header = emp_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            job_function = job_header.find_next_sibling("span").text.strip()
            job_post["job_function"] = job_function
            
        except:
            job_post["job_function"] = None
            
        # Industries
        try:
            level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
            emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            job_header = emp_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            industry_header = job_header.find_next("h3", {"class": "description__job-criteria-subheader"})
            industry = industry_header.find_next_sibling("span").text.strip()
            job_post["industry"] = industry

        except:
            job_post["industry"] = "Job type not specified"
        
        # Years of Experience - Keep as given in description
        try:
            bullet_points = raw_description.find_all(["li", "p"])
            pattern = r'(\d+)\+?\s*years?\s*(?:of experience)?|(\d+)-(\d+)\s*years?\s*(?:of experience)?|(\d+)\s*years?\s*(?:of experience)?'

            matches = re.findall(pattern, cleaned_desc)
            yoe_bullets = []

            for bullet in bullet_points:
                text = bullet.get_text(strip=True)  
                if re.search(pattern, text):  
                    yoe_bullets.append(text)

            job_post["yoe"] = yoe_bullets
        except:
            job_post["yoe"] = None

        # Degree Required - format as a list if multiple degrees
        try:
            pattern = r"(?i)\b(bachelor['']?s|master['']?s|ph\.?d|doctorate|b\.?s\.?|m\.?s\.)\b"
            edu = re.findall(pattern, cleaned_desc)
            
            edu = [match.lower().replace("'", "'") for match in edu]
            degree_map = {"bs": "bachelor's", "ms": "master's", "b.s": "bachelor's", "m.s": "master's"}
            formatted_matches = [degree_map.get(match, match) for match in edu]
            degrees = list(set(formatted_matches))
            
            job_post["education"] = degrees
        except:
            job_post["education"] = None

        # Salary
        try:
            salary_div = job_soup.find("div", {"class": "salary compensation__salary"})
            if salary_div:  
                job_post["salary"] = salary_div.text.strip()
            else:
                if raw_description and hasattr(raw_description, 'text'):  # Check if raw_description is not None and has the 'text' attribute
                    pattern = r"\$[\d,]+(?:\.\d{2})?\s?-\s?\$[\d,]+(?:\.\d{2})?"
                    salary_range = re.findall(pattern, raw_description.text)
                    job_post["salary"] = " ".join(salary_range) if salary_range else None
                else:
                    job_post["salary"] = None

        except AttributeError as e:
            job_post["salary"] = None

        except:
            job_post["salary"] = None

        job_list.append(job_post)

    return job_list

# saving to json file, but can switch to sqlite later
def save_jobs_to_json(job_list: list, filename: str = "jobs.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(job_list, f, ensure_ascii=False, indent=2)






# Optional: test block
if __name__ == "__main__":
    #print("test")
    jobs = scrape_jobs("Data Scientist", "Los Angeles County", num_jobs=10)
    job_descriptions = [job['description'] for job in jobs]
    embeddings = embed_jobs(job_descriptions, method="sbert")
   