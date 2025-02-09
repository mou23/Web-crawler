import re
import os
import csv
import json
from hashlib import sha256
from datetime import datetime
from bs4 import BeautifulSoup
import utils.text_processor as tp
from utils.validation import is_valid_scheme, is_valid_file, is_valid_domain, pagination_trap
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode, urljoin, urldefrag
from utils.simhash import SimhashDBManager
from utils import get_logger

logger = get_logger("FILTER")

def scraper(url, resp):
    simhash_db = SimhashDBManager()

    if resp.status != 200 or resp.raw_response is None:
        return []
    
    page_raw_response = resp.raw_response.content.decode('utf-8', errors='ignore')
    if tp.low_value_page(url, page_raw_response):
        return []
    
    page_text_only_content = tp.get_text_content_only(page_raw_response)
    if simhash_db.lib_is_duplicate(url, page_text_only_content):
        return []

    store_content(url, page_raw_response)
    links = extract_next_links(url, resp) 
    return [link for link in links if is_valid(link)]

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
        try:
            absolute_url = urljoin(url, a_tag["href"])
            cleaned_url = _clean_url(absolute_url)
            links.append(cleaned_url)
        except Exception as e:
            logger.info(f"Error extracting link {absolute_url} from {url}: {e}")
    
    return links

def _clean_url(url):
    url, _ = urldefrag(url)  # Remove fragment
    url = _filter_and_sort_query_params(url)  # Sort query parameters

    return url

def _filter_and_sort_query_params(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    IGNORE_PARAMS = {"filter", "tab_", "image", "sort", "order", "from", "to", "limit"}
    filtered_params = {k: v for k, v in query_params.items() if not any(k.startswith(ignore) for ignore in IGNORE_PARAMS)}

    sorted_query = urlencode(sorted(filtered_params.items()), doseq=True)
    normalized_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                 parsed.params, sorted_query, parsed.fragment))
    
    return normalized_url

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

def store_content(url, content):
    current_time = datetime.now().timestamp()
    url_hash = sha256(url.encode()).hexdigest()
    filename = os.path.join("pages", f"{url_hash}.json")

    data = {
        "url": url,
        "timestamp": current_time,
        "content": content
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
