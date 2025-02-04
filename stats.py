import os
import json
from typing import Set
from urllib.parse import urlparse

def get_unique_pages(pages_dir: str = 'pages') -> int:
    return len(os.listdir(pages_dir))

def get_unique_domains(pages_dir: str = 'pages') -> Set[str]:
    unique_domains = set()

    for filename in os.listdir(pages_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(pages_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    url = data['url']  
                    domain = urlparse(url).netloc 
                    unique_domains.add(domain)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {filename}: {e}")

    return unique_domains

def main():
    dir = "pages/"

    print("[*] Unique pages: ", get_unique_pages(dir))

    # TODO fix
    unique_domains = get_unique_domains(dir)
    print("[*] Unique domains: ", len(unique_domains))
    for domain in unique_domains:
        print(domain)

if __name__ == '__main__':
    main()