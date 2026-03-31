import requests
import json
from typing import List, Dict
from datetime import datetime
import re
import os
from dotenv import load_dotenv

# class AdzunaScraper:
    # def __init__(self):
    #     self.app_id = os.getenv('ADZUNA_APP_ID')
    #     self.app_key = os.getenv('ADZUNA_APP_KEY')
    #     self.base_url = "https://api.adzuna.com/v1/api/jobs"

    
load_dotenv()

APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')

base_url = "https://api.adzuna.com/v1/api/jobs"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "what": "data scientist",
    "where": "New York",
    "results_per_page": 1,
    "content-type": "application/json"
}

response = requests.get(base_url, params=params)
data = response.json()

# Check if we got any jobs back
if data.get("results"):
    job = data["results"][0]
    print("Job details:\n")
    for key, value in job.items():
        print(f"{key}: {value}")
else:
    print("No jobs found.")