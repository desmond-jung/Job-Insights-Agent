import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def validate_careers_url(url, keywords=None, timeout=2):
    if keywords is None:
        keywords = ["careers", "jobs", "join-us", "join", "work-with-us", "work-here", "opportunities", "open-positions", "employment", "hiring", "vacancies", "job-openings", "career-opportunities", "job-listings", "apply", "talent", "people", "we-are-hiring", "team", "career-center", "job-board", "recruiting", "career-opportunity", "life-at", "our-team", "current-openings"
]
    try:
        # Use HEAD first for speed
        head = requests.head(url, timeout=timeout, allow_redirects=True)
        if head.status_code != 200:
            return False
        # Only do GET if HEAD is OK and URL contains a keyword
        url_lower = url.lower()
        if any(kw in url_lower for kw in keywords):
            return True
        # If not in URL, do a minimal GET and check content
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return False
        text = resp.text.lower()
        return any(kw in text for kw in keywords)
    except Exception as e:
        print(f"Error for {url}: {e}")
        return False


def discover_careers_url(website_url, timeout=2, max_candidates=5):
    keywords = ["careers", "jobs", "join-us", "join", "work-with-us", "work-here", "opportunities", "open-positions", "employment", "hiring", "vacancies", "job-openings", "career-opportunities", "job-listings", "apply", "talent", "people", "we-are-hiring", "team", "career-center", "job-board", "recruiting", "career-opportunity", "life-at", "our-team", "current-openings"
]
    # 1. Try common patterns first (no more than 3 requests)
    patterns = ["/careers", "/jobs", "/work-with-us"]
    for pattern in patterns:
        candidate = urljoin(website_url, pattern)
        if validate_careers_url(candidate, keywords, timeout):
            return candidate

    # 2. Scrape homepage ONCE and collect candidate links
    try:
        resp = requests.get(website_url, timeout=timeout)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(" ", strip=True).lower()
            # Only consider links with a keyword in href or text
            if any(kw in href or kw in text for kw in keywords):
                abs_url = urljoin(website_url, a["href"])
                links.append((abs_url, href, text))
        # Score and sort links: prioritize short URLs and those with 'career' or 'job'
        def score(link):
            url, href, text = link
            score = 0
            if "career" in href or "career" in text:
                score += 2
            if "job" in href or "job" in text:
                score += 1
            score -= len(url)  # shorter is better
            return score
        links = sorted(links, key=score, reverse=True)
        # Only check the top N candidates
        for abs_url, _, _ in links[:max_candidates]:
            if validate_careers_url(abs_url, keywords, timeout):
                return abs_url
    except Exception:
        pass
    return None

if __name__ == "__main__":
    print(validate_careers_url("https://tesla.com/careers"))
