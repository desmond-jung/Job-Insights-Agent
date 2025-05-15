import requests
import time
from bs4 import BeautifulSoup
import re
import json
import openai

def clean_description(description):
    if description:
        description = description.text
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', description)
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    return None

def enrich_job_metadata(job_dict: dict, salary_found: bool = True) -> dict:
    """
    Enrich job data dictionary with fields years of experinece, salary
    """
    if not job_dict.get('description'):
        return job_dict
    
    try:
        prompt = f"""
        Given the raw job description of the job listing page, extract the necessary years of experience required for this job.
        If multiple ranges or number of years of experience are given, average the numbers. 
        Look for phrases like "X years of experience", "minimum X years", "X+ years", etc.
        If a specific number is mentioned (like "1 years of work experience"), use that number.

        Some example of years of experience are:
        3+ years of experience in data analysis -> 3  
        At least 5 years of relevant experience -> 5  
        Minimum 2 years experience working with Python -> 2  
        4 to 6 years of experience in project management -> 5   
        Must have 2 years' experience in customer support, 4 years in cloud -> 3  
        Experience of 1 year or more with data pipelines -> 1  
        Over 8 years of experience in software development -> 8  
        5+ yrs in a leadership role -> 5  
        1 years of work experience -> 1
        
        Additionally, extract the salary range provided in the text. If the salary is given in hourly rates, convert it to salary.
        Here are some examples:

        Salary starts at $90,000 per year -> 90000  
        We offer a competitive salary of $120k–$140k depending on experience -> 130000  
        Compensation: $30/hour, full-time position -> 62400  
        Base salary of $100,000 with performance bonuses -> 100000  
        Earn between $70,000 and $90,000 annually -> 80000  
        The role pays $5,000 per month -> 60000  
        Salary range: $95K to $115K -> 105000  
        Annual compensation of $110k+ based on skills -> 110000  
        Pay starts at $45/hour for experienced candidates -> 93600  
        $80,000/year minimum, with equity options -> 80000  
        You'll earn about $65,000 to $85,000 depending on fit -> 75000  
        Our starting salary is $75,000 -> 75000  
        Hourly wage between $50 and $60 -> 114400 
        
        Return a JSON object with only these fields:
        yoe (number or null), salary_range(string or null)

        Job Description:
        {job_dict['description']}
        """
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful job assistant that extracts job metadata from a job posting description. Return a JSON object ONLY"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        result = response.choices[0].message.content.strip()
        metadata = json.loads(result)

        if salary_found:
            job_dict.update({
            'years_experience': metadata.get('yoe')})
        else:
            job_dict.update({
                'years_experience': metadata.get('yoe'),
                'salary_range': metadata.get('salary_range')
            })
    except Exception as e:
        print(f"Error enriching job metadata: {str(e)}")
        # Add empty fields if enrichment fails
        job_dict.update({
            'years_experience': None,
            'salary_range': None
        })
    return job_dict

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

        job_post["job_id"] = job_id
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

        # Seniority Level
        try:
            level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
            sen_level = level_header.find_next_sibling("span").text.strip()
            job_post["seniority_level"] = sen_level
        except:
            job_post["seniority_level"] = None
            
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
            
        # Salary
        salary_found = False
        try:
            salary_div = job_soup.find("div", {"class": "salary compensation__salary"})
            if salary_div:  
                job_post["salary"] = salary_div.text.strip()
                salary_found = True
        except:
            job_post["salary"] = None
            salary_found = False

        job_post = enrich_job_metadata(job_post, salary_found)
        job_list.append(job_post)

    return job_list


    
# Optional: test block
if __name__ == "__main__":
    jobs = scrape_jobs(num_jobs=1)
    print(f"Scraped {len(jobs)} jobs")
    print(json.dumps(jobs[0], indent=2))

    
   