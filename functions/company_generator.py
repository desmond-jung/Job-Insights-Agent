import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_company_list():

    prompt = (
        "Generate a list of 2 diverse companies based in the United States in JSON array form, "
        "with each object containing: {'name': ...}. "
        "Include companies from a wide range of industries (technology, healthcare, finance, manufacturing, retail, energy, etc.), "
        "and of all sizes (large corporations, mid-sized firms, and small businesses/startups). "
        "Draw from sources such as the Fortune 500, Inc. 5000, Forbes Global 2000 (U.S.-based only), Crunchbase, Y Combinator startups, "
        "NASDAQ and NYSE-listed companies, as well as lesser-known and regionally diverse companies. "
        "Ensure the list is as comprehensive and varied as possible. "
        "Return only the JSON array, with no extra text or explanation. "
        "If you cannot fit all companies, prioritize diversity and maximize the number of unique entries."
    )
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a business researcher"},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    try:
        companies = json.loads(content)
    except json.JSONDecodeError:
        # Extract JSon from text if LLM adds extra text
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            companies = json.loads(match.group(0))
        else:
            raise ValueError("Could not parse company list from LLM response.")
        
    return companies

def enrich_company_data(company_list: list, fields:list = ["domain", "careers_page_url", "industry"]):
    prompt = (
        "Given the following list of companies, add the following fields for each company:"
        f"{', '.join(fields)}."
        "For 'careers_page_url', find the landing page that has all the individual job listings"
        "Return the enriched list as a JSON array, with no extra text or explanation. \n"
        f"Companies: {json.dumps(company_list)}"
    )
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a business researcher."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    try:
        enriched = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            enriched = json.loads(match.group(0))
        else:
            raise ValueError("Could not parse enriched company list from LLM response.")
    return enriched

if __name__ == "__main__":
    companies = generate_company_list()
    print(companies)
    print(enrich_company_data(companies))

    #https://www.tesla.com/careers/search/?site=US 