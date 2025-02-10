from urllib.parse import urlparse

def _get_three_level_domain(url):
    netloc = urlparse(url).netloc  # Extract netloc (e.g., deep.sub.example.com)
    parts = netloc.split('.')  
    if len(parts) >= 3:  
        return ".".join(parts[-3:])  # Keep last three parts (e.g., sub.example.com)
    return netloc  # Return as is if already three levels or less