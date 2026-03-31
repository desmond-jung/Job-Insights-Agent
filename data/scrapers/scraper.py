import requests
import time
from bs4 import BeautifulSoup
import re
import json
import spacy
from keybert import KeyBERT
import subprocess



def clean_description(description):
    if description:
        description = description.text

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

def extract_job_url(job_soup):
    a_tag = job_soup.find("a", {"class": 'topcard__link'})
    return a_tag.get('href') if a_tag.get('href') else None

    
def extract_title(job_soup):
    title = job_soup.find("h2", {"class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip() if job_soup.find("h2", {"class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}) else None
    return title 

def extract_company_name(job_soup):
    company_name = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip() if job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}) else None
    return company_name

def extract_location(job_soup):
    location = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip() if job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}) else None
    if not location:
        return {"location": None, "city": None, "state": None, "country": None}
    if location == "United States":
        return {"location": location, "city": None, "state": None,"country": "United States"}
    
    location = location.replace(" Metropolitan Area", "")

    parts = [part.strip() for part in location.split(",")]

    result = {
        "location": location,
        "city": None,
        "state": None,
        "country": "United States"
    }

    if len(parts) >= 1:
        result["city"] = parts[0]
    
    if len(parts) >= 2:
        # Handle state abbreviations and full names
        state = parts[1]
        # Remove any extra spaces
        state = state.strip()
        result["state"] = state
    
    return result

def extract_remote_status(job_soup, title, location, description):
    """Extract whether job allows for remote work"""
    try:
        remote_keywords = ['remote', 'work from home', 'wfh', 'virtual']
        if title and any(keyword in title.lower() for keyword in remote_keywords):
            return 1

        if location and location.lower() == 'remote':
            return 1
        if description:
            remote_phrases = [
                'remote work', 'work remotely', 'work from home', 'wfh',
                'virtual position', 'remote position', 'remote role',
                'work from anywhere', 'remote-first', 'remote friendly'
            ]
            if any(phrase in description for phrase in remote_phrases):
                return 1
        return 0
    except:
        return 0

def extract_industry(job_soup):
    try:
        level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
        emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
        job_header = emp_header.find_next("h3", {"class": "description__job-criteria-subheader"})
        industry_header = job_header.find_next("h3", {"class": "description__job-criteria-subheader"})
        industry = industry_header.find_next_sibling("span").text.strip()
        return industry
    except:
        return None
    
def extract_seniority_level(job_soup):
    try:
        level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
        sen_level = level_header.find_next_sibling("span").text.strip()
        return sen_level
    except:
        return None
def extract_employment_type(job_soup):
    try:
        level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
        emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
        emp_type = emp_header.find_next_sibling("span").text.strip()
        return emp_type
        
    except:
        return None
    
def extract_job_function(job_soup):
    try:
        level_header = job_soup.find("h3", {"class": "description__job-criteria-subheader"})
        emp_header = level_header.find_next("h3", {"class": "description__job-criteria-subheader"})
        job_header = emp_header.find_next("h3", {"class": "description__job-criteria-subheader"})
        job_function = job_header.find_next_sibling("span").text.strip()
        return job_function
        
    except:
        return None
    
def extract_salary(job_soup, description):
    """Extract salary information with detailed fields."""
    try:
        # First try to find salary in the dedicated div
        salary_div = job_soup.find("div", {"class": "salary compensation__salary"})
        if salary_div:
            salary_text = salary_div.text.strip()
            # Try to parse range first
            range_pattern = r"\$([\d,]+)(?:\.\d{2})?\s?-\s?\$([\d,]+)(?:\.\d{2})?"
            range_match = re.search(range_pattern, salary_text)
            
            if range_match:
                min_salary = int(range_match.group(1).replace(',', ''))
                max_salary = int(range_match.group(2).replace(',', ''))
                return {
                    "salary_raw": salary_text,
                    "salary_min": int(min_salary),
                    "salary_max": int(max_salary),
                    "salary_avg": (min_salary + max_salary) / 2
                }
            
            # Try to find single number
            single_pattern = r"\$([\d,]+)(?:\.\d{2})?"
            single_match = re.search(single_pattern, salary_text)
            if single_match:
                salary = int(single_match.group(1).replace(',', ''))
                return {
                    "salary_raw": salary_text,
                    "salary_min": int(salary),
                    "salary_max": int(salary),
                    "salary_avg": salary
                }
        
        # If no salary in div, try description
        if description and hasattr(description, 'text'):
            # Try to find range in description
            range_pattern = r"\$([\d,]+)(?:\.\d{2})?\s?-\s?\$([\d,]+)(?:\.\d{2})?"
            range_match = re.search(range_pattern, description.text)
            
            if range_match:
                min_salary = int(range_match.group(1).replace(',', ''))
                max_salary = int(range_match.group(2).replace(',', ''))
                return {
                    "salary_raw": range_match.group(0),
                    "salary_min": int(min_salary),
                    "salary_max": int(max_salary),
                    "salary_avg": (min_salary + max_salary) / 2
                }
            
            # Try to find single number in description
            single_pattern = r"\$([\d,]+)(?:\.\d{2})?"
            single_match = re.search(single_pattern, description.text)
            if single_match:
                salary = int(single_match.group(1).replace(',', ''))
                return {
                    "salary_raw": single_match.group(0),
                    "salary_min": int(salary),
                    "salary_max": int(salary),
                    "salary_avg": salary
                }
        
        # If no salary found
        return {
            "salary_raw": None,
            "salary_min": None,
            "salary_max": None,
            "salary_avg": None
        }

    except Exception as e:
        return {
            "salary_raw": None,
            "salary_min": None,
            "salary_max": None,
            "salary_avg": None
        }

def extract_yoe(job_soup, description):
    """Extract years of experience with detailed fields."""
    try:
        # First try bullet points for precise matches
        bullet_points = description.find_all(["li", "p"])
        experience_keywords = [
            'experience', 'exp', 'minimum', 'at least', 'required',
            'qualification', 'background', 'track record', 'proven',
            'demonstrated', 'expertise', 'proficiency'
        ]
        
        yoe_bullets = []
        numbers_found = []
        
        # Check bullet points first
        for bullet in bullet_points:
            text = bullet.get_text(strip=True).lower()
            if not text:
                continue
                
            # Look for ranges first (e.g., "3-5 years", "3 to 5 years")
            range_pattern = r'(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?|yrs?)(?:\s+of\s+experience)?'
            range_match = re.search(range_pattern, text)
            
            if range_match and any(keyword in text for keyword in experience_keywords):
                yoe_bullets.append(text)
                min_years = int(range_match.group(1))
                max_years = int(range_match.group(2))
                return {
                    "yoe_raw": text,
                    "yoe_min": min_years,
                    "yoe_max": max_years,
                    "yoe_avg": (min_years + max_years) / 2
                }
            
            # Look for single numbers
            numbers = re.findall(r'\d+', text)
            if numbers and any(keyword in text for keyword in experience_keywords):
                yoe_bullets.append(text)
                numbers_found.extend([int(num) for num in numbers])
        
        # If no matches in bullets, try full description
        if not numbers_found:
            # Try to find ranges in the full description
            range_pattern = r'(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?|yrs?)(?:\s+of\s+experience)?'
            range_match = re.search(range_pattern, clean_description(description))
            
            if range_match:
                min_years = int(range_match.group(1))
                max_years = int(range_match.group(2))
                return {
                    "yoe_raw": range_match.group(0),
                    "yoe_min": min_years,
                    "yoe_max": max_years,
                    "yoe_avg": (min_years + max_years) / 2
                }
            
            # Try to find single numbers
            pattern = r'(?:experience|exp|minimum|at least|required):?\s*(\d+)\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?'
            matches = re.findall(pattern, clean_description(description))
            if matches:
                numbers_found = [int(num) for num in matches]
        
        # If we found single numbers, calculate average
        if numbers_found:
            avg_years = sum(numbers_found) / len(numbers_found)
            return {
                "yoe_raw": str(numbers_found[0]) if len(numbers_found) == 1 else str(numbers_found),
                "yoe_min": None,
                "yoe_max": None,
                "yoe_avg": avg_years
            }
            
        return {
            "yoe_raw": None,
            "yoe_min": None,
            "yoe_max": None,
            "yoe_avg": None
        }
            
    except Exception as e:
        return {
            "yoe_raw": None,
            "yoe_min": None,
            "yoe_max": None,
            "yoe_avg": None
        }
    
def extract_education(job_soup, description):
# Degree Required - format as a list if mulitple degrees

    try:
        pattern = r"(?i)\b(bachelor[’']?s|master[’']?s|ph\.?d|doctorate|b\.?s\.?|m\.?s\.)\b"
        edu = re.findall(pattern, description)
        
        edu = [match.lower().replace("’", "'") for match in edu]
        degree_map = {"bs": "bachelor's", "ms": "master's", "b.s": "bachelor's", "m.s": "master's"}
        formatted_matches = [degree_map.get(match, match) for match in edu]
        degrees = list(set(formatted_matches))     
        return degrees
    
    except:
        return []

# def extract_skills(job_descriptions):
#     try:
#         nlp = spacy.load("en_core_web_sm")
#     except OSError:
#         subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
#         nlp = spacy.load("en_core_web_sm")
#     kw_model = KeyBERT()
#     keywords = kw_model.extract_keywords(job_descriptions, keyphrase_ngram_range=(1, 3), stop_words='english')
#     skills = [kw for kw, score in keywords]
#     return skills

def get_job_ids(num_jobs: int = 50) -> list:
    """Get a list of job IDs from LinkedIn job listings."""
    all_jobs = []
    jobs_found = 0
    start_position = 0
    max_retries = 3
    retry_delay = 10  # seconds

    # Scrape job listing pages
    while jobs_found < num_jobs:
        list_url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords=&location=&f_TPR=r2592000&f_WT=2&start={start_position}"  # Added f_WT=2 for remote jobs
        )
        
        # Try multiple times if we get rate limited
        for attempt in range(max_retries):
            response = requests.get(list_url)
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                print(f"Rate limited. Waiting {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed to fetch page {start_position//10 + 1}. Status code: {response.status_code}")
                time.sleep(5)
        
        if response.status_code != 200:
            print("Max retries reached. Stopping job collection.")
            break
            
        list_data = response.text
        list_soup = BeautifulSoup(list_data, "html.parser")
        more_jobs = list_soup.find_all("li")
        
        if not more_jobs:
            print(f"No more jobs found at position {start_position}")
            break
            
        remaining_jobs = num_jobs - jobs_found
        jobs_to_add = more_jobs[:remaining_jobs]
        all_jobs.extend(jobs_to_add)
        jobs_found += len(jobs_to_add)
        
        #print(f"Found {len(jobs_to_add)} jobs on page {start_position//10 + 1}")
        #print(f"Total jobs found so far: {jobs_found}")
        
        if len(more_jobs) < 10:
            print("Last page reached")
            break
            
        start_position += 10
        time.sleep(2)  # Add small delay between pages

    # Extract job IDs
    job_id_list = []
    for job in all_jobs:
        base_card_div = job.find("div", {"class": "base-card"})
        if base_card_div:
            job_id = base_card_div.get("data-entity-urn", "")
            if job_id:
                job_id = job_id.split(":")[3]
                job_id_list.append(job_id)
    
    return list(set(job_id_list))

def extract_job_source(job_url):
    """Extract the source from the job URL."""
    try:
        if not job_url:
            return None
            
        # Remove http(s):// and www. if present
        url = job_url.lower()
        url = re.sub(r'^https?://(www\.)?', '', url)
        
        # Split by first /
        parts = url.split('/', 1)
        if len(parts) > 1:
            return parts[0]  # Returns domain like 'linkedin.com'
        return None
    except:
        return None

def scrape_jobs(num_jobs: int = 50) -> list:
    """Scrape job details for the given number of jobs."""
    # Get job IDs first
    job_id_list = get_job_ids(num_jobs)
    print(f"Found {len(job_id_list)} unique job IDs")

    # Scrape jobs sequentially
    job_list = []
    for job_id in job_id_list:
        try:
            job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
            response = requests.get(job_url)
            
            if response.status_code != 200:
                print(f"Failed to fetch job {job_id}. Status code: {response.status_code}")
                continue
                
            job_soup = BeautifulSoup(response.text, "html.parser")
            job_post = {}

            # Descriptions
            raw_description = job_soup.find("div", {"class": "description__text description__text--rich"})
            cleaned_desc = clean_description(raw_description)

            # Extract all job details
            job_post["job_id"] = job_id
            job_post["job_url"] = extract_job_url(job_soup)
            job_post["source"] = extract_job_source(job_post["job_url"])
            job_post["title"] = extract_title(job_soup)
            job_post["company_name"] = extract_company_name(job_soup)
            job_post["location"] = extract_location(job_soup)['location']
            job_post["city"] = extract_location(job_soup)['city']
            job_post["state"] = extract_location(job_soup)['state']
            job_post["country"] = extract_location(job_soup)['country']
            job_post["remote"] = extract_remote_status(job_soup, extract_title(job_soup), extract_location(job_soup)['location'], cleaned_desc)
            job_post["description"] = cleaned_desc
            job_post['industry'] = extract_industry(job_soup)
            job_post['seniority_level'] = extract_seniority_level(job_soup)
            job_post['employment_type'] = extract_employment_type(job_soup)
            job_post['job_function'] = extract_job_function(job_soup)
            
            # Extract salary with all fields
            salary_data = extract_salary(job_soup, raw_description)
            job_post['salary_raw'] = salary_data['salary_raw']
            job_post['salary_min'] = salary_data['salary_min']
            job_post['salary_max'] = salary_data['salary_max']
            job_post['salary_avg'] = salary_data['salary_avg']
            
            # Extract YOE with all fields
            yoe_data = extract_yoe(job_soup, raw_description)
            job_post['yoe_raw'] = yoe_data['yoe_raw']
            job_post['yoe_min'] = yoe_data['yoe_min']
            job_post['yoe_max'] = yoe_data['yoe_max']
            job_post['yoe_avg'] = yoe_data['yoe_avg']
            
            job_post['education'] = extract_education(job_soup, cleaned_desc)
            #job_post['skills'] = extract_skills(cleaned_desc)

            job_list.append(job_post)
            #print(f"Successfully scraped job {job_id} - {job_post.get('title')}")
            
            # Add a small delay between requests
            time.sleep(2)
            
        except Exception as e:
            print(f"Error scraping job {job_id}: {str(e)}")
            continue
    
    return job_list

# Optional: test block
if __name__ == "__main__":
    start_time = time.time()
    
    jobs = scrape_jobs(num_jobs=1)
    print(f"Scraped {len(jobs)} jobs")
    
    for job in jobs:
        # Create a copy of the job dictionary without the description
        job_details = {k: v for k, v in job.items() if k != 'description'}
        print("\nJob Details:")
        for key, value in job_details.items():
            print(f"{key}: {value}")
    
    end_time = time.time()
    print(f"\nTime taken: {end_time - start_time:.2f} seconds")
   

    
   