import spacy
import sklearn
import flask
import pandas as pd
from collections import Counter
from typing import List, Dict, Tuple
import re
from functions.database import get_all_jobs
from keybert import KeyBERT

# load spacy modek
def extract_skills(job_descriptions):
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model...")
        import subprocess
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")


    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(job_descriptions, keyphrase_ngram_range=(1, 3), stop_words='english')
    skills = [kw for kw, score in keywords]
    return skills
