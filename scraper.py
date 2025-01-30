import re
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from hashlib import sha256
from utils.validation import is_valid_scheme, is_valid_file, is_valid_domain, pagination_trap

def scraper(url, resp):
    current_time = datetime.now().timestamp()

    if (resp.status== 200):
        # TODO check valid content
        store_content(url, resp.raw_response.content, current_time)
        links = extract_next_links(url, resp)

        return [link for link in links if is_valid(link)]

    return []

def extract_next_links(url, resp):
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []
    
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    for a_tag in soup.find_all("a", href=True):
        absolute_url = urljoin(url, a_tag["href"])
        url_without_fragment, _ = urldefrag(absolute_url)
        links.append(url_without_fragment)
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    try:
        parsed = urlparse(url)
        
        return is_valid_scheme(parsed) and \
               is_valid_file(parsed) and \
               is_valid_domain(parsed) and \
               not pagination_trap(parsed)

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    except Exception as e:
        print ("Exception when validating url:", e)

def store_content(url, content, current_time):
    os.makedirs("pages", exist_ok=True)
    url_hash = sha256(url.encode()).hexdigest()
    filename = os.path.join("pages", f"{url_hash}.json")

    data = {
        "url": url,
        "timestamp": current_time,
        "content": content.decode('utf-8', errors='ignore')
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
