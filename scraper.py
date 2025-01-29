import re
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from hashlib import sha256

def scraper(url, resp):
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
    current_time = datetime.now().timestamp()
    links = []
    if (resp.status== 200):
        print(url)
        store_content(url, resp.raw_response.content, current_time)
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            absolute_url = urljoin(url, a_tag["href"])
            url_without_fragment, _ = urldefrag(absolute_url)
            links.append(url_without_fragment)
            print(url_without_fragment, is_valid(url_without_fragment))
    
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        allowed_domains = [
            "ics.uci.edu", 
            "cs.uci.edu", 
            "informatics.uci.edu", 
            "stat.uci.edu",
            "today.uci.edu"
        ]
        
        if not any(parsed.hostname.endswith(domain) for domain in allowed_domains):
            return False
        
        if parsed.hostname == "today.uci.edu" and not parsed.path.startswith("/department/information_computer_sciences/"):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

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
    print(f"Saved content to {filename}")
