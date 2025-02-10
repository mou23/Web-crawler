import os
import re
import json
import time
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
from urllib.parse import urldefrag, urlparse

def extract_urls_and_contents(directory):
    urls = []
    text_contents = {}

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            
            urls.append(data["url"])
            soup = BeautifulSoup(data["content"], "html.parser")
            text_contents[filename] = soup.get_text(separator=" ", strip=True)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading {filename}: {e}")

    return urls, text_contents

def unique_pages(urls):
    return sorted(set(urls))

def get_subdomain_counts(urls):
    subdomain_counts = defaultdict(set)
    for url in urls:
        cleaned_url = urldefrag(url)[0]
        parsed_url = urlparse(cleaned_url)
        subdomain = parsed_url.netloc
        if "ics.uci.edu" in parsed_url.netloc:
            subdomain_counts[subdomain].add(cleaned_url)
    
    return subdomain_counts
    
def get_top_longest_pages(urls, text_contents, top_n=5):
    page_lengths = []

    for url, text in zip(urls, text_contents.values()):
        word_count = len(text.split())
        page_lengths.append((url, word_count))

    page_lengths.sort(key=lambda x: x[1], reverse=True)
    top_pages = page_lengths[:top_n]

    return top_pages

def get_words(text):
    lower_case_words = []
    try:
        all_words = re.split("[^a-zA-Z0-9]+", text)
        for word in all_words:
            if len(word) > 0:
                lower_case_words.append(word.lower())
    except Exception as e:
        print(e)
    
    return lower_case_words

def get_stop_words(filename):
    with open(filename, encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()
    return set([line.strip() for line in lines])

def get_most_common_words(text_contents, stop_words, n=50):
    word_counter = []
    
    for text in text_contents.values():
        words = get_words(text)

        for word in words:
            if word not in stop_words:
                word_counter.append(word)

    return Counter(word_counter).most_common(n)
    

directory_path = "pages"
urls, text_contents = extract_urls_and_contents(directory_path)

# Q1. How many unique pages did you find?
uniq_urls = unique_pages(urls)
print(f'\n### Number of unique pages {uniq_urls}) ###')
for url in uniq_urls:
    print(url)


# Q2. What is the longest page in terms of number of words?
top5 = get_top_longest_pages(urls, text_contents)
print("\n### Top longest pages ###")
for idx, (url, count) in enumerate(top5, 1):
    print(f"{idx}. {url} with {count} words")

# Q3. What are the 50 most common words in the entire corpus?
stop_words = get_stop_words('stop_words.txt')
common_words = get_most_common_words(text_contents, stop_words)
print('\n### Most common words ###')
for word, count in common_words:
    print(f"{word}: {count}")

# Q4. How many subdomains did you find in the ics.uci.edu domain?
subdomains = get_subdomain_counts(urls)
print('\n### ics.uci.edu subdomain count ###')
for k, v in sorted(subdomains.items(), key=lambda x: x[0]):
    print(f"{k}: {len(v)}")

# start_time = time.time()
# end_time = time.time()
# elapsed_time = end_time - start_time
# print(f"Elapsed time: {elapsed_time} seconds")