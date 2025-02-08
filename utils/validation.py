from urllib.parse import parse_qs
import re

def is_valid_scheme(parsed_url):
    if parsed_url.scheme not in set(["http", "https"]):
        return False
    return True

def is_valid_file(parsed_url):
    return not re.match(
        r".*\.(css|js|bmp|gif|jpe?g|ico|img"
        + r"|png|tiff?|mid|mp2|mp3|mp4"
        + r"|wav|avi|mov|mpg|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        + r"|ps|eps|tex|ppt|pptx|pps|ppsx|doc|docx|xls|xlsx|names"
        + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|ics"
        + r"|epub|dll|cnf|tgz|sha1"
        + r"|thmx|mso|arff|rtf|jar|csv"
        + r"|java|py|ipynb|jsp"
        + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed_url.path.lower())

def is_valid_domain(parsed_url):
    #"cs.uci.edu", 
    #"informatics.uci.edu", 
    #"today.uci.edu"
    allowed_domains = [
        "ics.uci.edu", 
        "cs.uci.edu", 
        "informatics.uci.edu", 
        "stat.uci.edu"
    ]
    
    hostname = parsed_url.hostname
    if not hostname:
        return False

    # Remove 'www.' prefix if present
    if hostname.startswith("www."):
        hostname = hostname[4:]
    
    # Check if the hostname ends with any allowed domain or is a subdomain of an allowed domain
    if any(hostname == domain or hostname.endswith(f".{domain}") for domain in allowed_domains):
        return True
    
    return False

def pagination_trap(parsed_url):
    pagination_threshold = 1000
    query_params = parse_qs(parsed_url.query)

    # Detect numeric query parameters (e.g., ?page=1000)
    num_values = [v for k, v in query_params.items() if k in {'page', 'offset', 'start'}]
    if any(int(v[0]) > pagination_threshold for v in num_values if v[0].isdigit()):
        return True

    # Detect patterns in URL path like /page/1000/
    if match := re.search(r'/page/(\d+)/', parsed_url.path):
        page_number = int(match.group(1))
        if page_number > pagination_threshold:
            return True
    
    ### Known Specific Cases ###
    if parsed_url.netloc == "wics.ics.uci.edu":
        if re.search(r"/events/category/wics-bonding/\d{4}-\d{2}", parsed_url.path) or \
                "/events/category/wics-bonding/day" in parsed_url.path:
            return True

    return False