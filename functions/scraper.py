import requests
import time
from bs4 import BeautifulSoup
import re
import json
import openai
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def clean_description(description):
    if description:
        description = description.text
        # First add spaces between camelCase
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', description)
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation except periods
        text = re.sub(r'[^\w\s.]', '', text)
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Clean up multiple periods
        text = re.sub(r'\.+', '.', text)
        # Clean up spaces around periods
        text = re.sub(r'\s*\.\s*', '. ', text)
        text = text.strip()
        return text
    return None

def extract_relevant_sentences(description: str) -> str:
    """
    Extract sentences that pertain to salary or years of experience
    """
    if not description:
        return ""
        
    sentences = description.split('.')
    relevant_sentences = []

    keywords = {
        'experience': [
            'year', 'years', 'experience', 'exp', 'minimum', 'least', 'required',
            'qualification', 'qualify',
            'background', 'track record', 'proven', 'demonstrated'
        ],
        'salary': [
            'salary', 'compensation', 'pay', 'wage', 'hourly', 'annual', '$', 
            'thousand', 'range', 'package', 'benefits', 'bonus', 'equity',
            'competitive'
        ]
    }

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:  # Skip empty sentences
            continue
            
        # Convert to lowercase for matching
        sentence_lower = sentence.lower()
        
        # For salary, only keep sentences with numbers and currency symbols
        if any(keyword in sentence_lower for keyword in keywords['salary']):
            if any(char.isdigit() for char in sentence):
                relevant_sentences.append(sentence)
        # For experience, keep sentences with keywords and numbers
        elif any(keyword in sentence_lower for keyword in keywords['experience']):
            if any(char.isdigit() for char in sentence):
                relevant_sentences.append(sentence)
    
    return '. '.join(relevant_sentences)

def enrich_job_metadata(job_dict: dict, salary_found: bool = True) -> dict:
    """
    Enrich job data dictionary with fields years of experinece, salary
    """
    if not job_dict.get('description'):
        return job_dict
    
    try:
        # Extract relevant sentences first
        relevant_text = extract_relevant_sentences(job_dict['description'])
        
        # Count tokens in the prompt
        prompt_tokens = count_tokens(relevant_text)
        print(f"Number of tokens in relevant text: {prompt_tokens}")
        print(f"Job ID: {job_dict.get('job_id')}")
        print(f"Original description length: {len(job_dict.get('description', ''))} characters")
        print(f"Relevant text length: {len(relevant_text)} characters")
        
        # LLM code (commented out for testing)
        
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful job assistant that extracts job metadata.\n"
                        "Extract years of experience and salary from the given text.\n"
                        "For experience: Look for numbers with 'year', 'experience', etc. Average if multiple numbers given.\n"
                        "For salary: Convert all amounts to annual salary (e.g., hourly*2080, monthly*12).\n"
                        "Return a JSON object with only these fields: yoe (number or null), salary_range (string or null)"
                    )
                },
                {"role": "user", "content": relevant_text}
            ],
            temperature=0.1
        )
        result = response.choices[0].message.content.strip()
        metadata = json.loads(result)

        if salary_found:
            job_dict.update({
                'years_experience': metadata.get('yoe')
            })
        else:
            job_dict.update({
                'years_experience': metadata.get('yoe'),
                'salary_range': metadata.get('salary_range')
            })
        
        
        # Don't actually call the API, just return the job dict
        return job_dict
    
    except Exception as e:
        print(f"Error enriching job metadata: {str(e)}")
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

    
   