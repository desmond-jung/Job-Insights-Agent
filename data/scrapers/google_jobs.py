import requests
import json
from typing import List, Dict
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def google_test():

    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'software engineer jobs',
        'num': 1,  # Just get 1 result
        'dateRestrict': 'm1'  # Last month
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            if 'items' in data and len(data['items']) > 0:
                # Get the first job result
                job = data['items'][0]
                print(job.keys())
                
            else:
                print("❌ No job results found")
                print(f"Response: {data}")
                
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    google_test()