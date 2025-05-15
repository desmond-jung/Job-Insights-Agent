import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import re

def ensure_https(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        parsed = parsed._replace(scheme="https")
        return urlunparse(parsed)
    return url

def validate_careers_url(url, keywords=None, timeout=2):
    url = ensure_https(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if keywords is None:
        keywords = ["careers", "jobs", "join-us", "join", "work-with-us", "work-here", "opportunities", "open-positions", "employment", "hiring", "vacancies", "job-openings", "career-opportunities", "job-listings", "apply", "talent", "people", "we-are-hiring", "team", "career-center", "job-board", "recruiting", "career-opportunity", "life-at", "our-team", "current-openings"]
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            #print(f"Non-200 status for {url}: {resp.status_code}")
            return False
        url_lower = url.lower()
        if any(kw in url_lower for kw in keywords):
            return True
        text = resp.text.lower()
        if "cloudflare" in text or "captcha" in text or "access denied" in text:
            #print(f"Blocked by bot protection at {url}")
            return False
        return any(kw in text for kw in keywords)
    except Exception as e:
        #print(f"Error for {url}: {e}")
        return False

def discover_careers_url(website_url, timeout=2, max_candidates=5):
    keywords = ["careers", "jobs", "join-us", "join", "work-with-us", "work-here", "opportunities", "open-positions", "employment", "hiring", "vacancies", "job-openings", "career-opportunities", "job-listings", "apply", "talent", "people", "we-are-hiring", "team", "career-center", "job-board", "recruiting", "career-opportunity", "life-at", "our-team", "current-openings"]
    website_url = ensure_https(website_url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # 1. Try common patterns first (no more than 3 requests)
    patterns = ["/careers", "/jobs", "/work-with-us"]
    for pattern in patterns:
        candidate = urljoin(website_url, pattern)
        if validate_careers_url(candidate, keywords, timeout):
            return candidate

    # 2. Scrape homepage ONCE and collect candidate links
    try:
        resp = requests.get(website_url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(" ", strip=True).lower()
            if any(kw in href or kw in text for kw in keywords):
                abs_url = urljoin(website_url, a["href"])
                links.append((abs_url, href, text))
        def score(link):
            url, href, text = link
            score = 0
            if "career" in href or "career" in text:
                score += 2
            if "job" in href or "job" in text:
                score += 1
            score -= len(url)
            return score
        links = sorted(links, key=score, reverse=True)
        for abs_url, _, _ in links[:max_candidates]:
            if validate_careers_url(abs_url, keywords, timeout):
                return abs_url
    except Exception as e:
        print(f"Error scraping homepage {website_url}: {e}")
        return None

if __name__ == "__main__":
    print(discover_careers_url("https://tesla.com/careers"))
