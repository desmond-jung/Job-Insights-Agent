import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def validate_careers_url(url, keywords=None, timeout=5):
    if keywords is None:
        keywords = ["career", "job", "work with us", "join our team", "employment", "vacancy", "opportunities", "positions", "join us", "openings"]
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return False
        url_lower = url.lower()
        # Accept if the URL itself contains a keyword
        if any(kw in url_lower for kw in keywords):
            return True
        text = resp.text.lower()
        return any(kw in text for kw in keywords)
    except Exception:
        return False
    
def discover_careers_url(website_url, timeout=5):
    patterns = [
        "/careers", "/jobs", "/careers.html", "/jobs.html", "/work-with-us", "/join-us", "/employment"
    ]
    for pattern in patterns:
        candidate = urljoin(website_url, pattern)
        if validate_careers_url(candidate, timeout=timeout):
            return candidate
    
    try:
        resp = requests.get(website_url, timeout=timeout)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(" ", strip=True).lower()
            if any(kw in href or kw in text for kw in ["career", "job", "work with us", "join our team", "employment", "vacancy"]):
                # Make absolute URL
                abs_url = urljoin(website_url, a["href"])
                if validate_careers_url(abs_url, timeout=timeout):
                    return abs_url
    except Exception:
        return None
    return None