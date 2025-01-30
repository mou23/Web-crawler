from urllib.parse import parse_qs
import re

def is_valid_scheme(parsed_url):
    if parsed_url.scheme not in set(["http", "https"]):
        return False
    return True

def is_valid_file(parsed_url):
    return not re.match(
        r".*\.(css|js|bmp|gif|jpe?g|ico"
        + r"|png|tiff?|mid|mp2|mp3|mp4"
        + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
        + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
        + r"|epub|dll|cnf|tgz|sha1"
        + r"|thmx|mso|arff|rtf|jar|csv"
        + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed_url.path.lower())

def is_valid_domain(parsed_url):
    allowed_domains = [
        "ics.uci.edu", 
        "cs.uci.edu", 
        "informatics.uci.edu", 
        "stat.uci.edu",
        "today.uci.edu"
    ]
    
    if not any(parsed_url.hostname.endswith(domain) for domain in allowed_domains):
        return False
    
    if parsed_url.hostname == "today.uci.edu" and not parsed_url.path.startswith("/department/information_computer_sciences/"):
        return False

    return True

def pagination_trap(parsed_url):
    pagination_threshold = 2000
    query_params = parse_qs(parsed_url.query)

    # Detect numeric query parameters (e.g., ?page=1000)
    num_values = [v for k, v in query_params.items() if k in {'page', 'offset', 'start'}]
    if any(int(v[0]) > pagination_threshold for v in num_values if v[0].isdigit()):
        return True  # Likely an infinite pagination trap

    # Detect patterns in URL path like /page/1000/
    if match := re.search(r'/page/(\d+)/', parsed_url.path):
        page_number = int(match.group(1))
        if page_number > pagination_threshold:
            return True

    return False