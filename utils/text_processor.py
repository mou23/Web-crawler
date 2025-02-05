from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from collections import Counter
import json
import os

#removes non-text tags
def get_text_content_only(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tags_to_remove = ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'svg', 'canvas','footer', 'ads', 'script', 'style']
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()  # Remove the tag from the tree

    # Return the cleaned HTML as a string
    text_content = soup.get_text(separator=' ', strip=True)
    return text_content


# get actual text to html text ratio
def text_to_html_content_ratio(html_content):
    actual_text = get_text_content_only(html_content)
    #soup = BeautifulSoup(htmlContent, 'html.parser')

    actual_text_length = len(actual_text)
    html_length = len(html_content)

    if html_length == 0: 
        return 0
    
    ratio = actual_text_length / html_length
    #print("The ration is" + str(ratio))
    return ratio


def is_unimportant_page(html_content):
    actual_text = get_text_content_only(html_content).lower()
    
    # check if text length is lower than a threshold
    if(len(actual_text) <= 100):
        return True

    # check if contains these messages
    messages = ["Sorry you dont have enough rights to read files",
     "Page does not exist", "Page not found"]
    for m in messages:
        if actual_text.contains(m.lower()):
            return True
    return False


def get_paragraphs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')  
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.get_text(strip='True'))
    return paragraphs

# Function to find duplicate paragraphs using fuzzy matching
def find_duplicates_by_fuzzy(paragraphs, similarity_threshold):
    
    normalized_paragraphs = []
    for p in paragraphs:
        p = p.lower().strip()
        words = p.split()
        normalized = ' '.join(words)
        normalized_paragraphs.append(normalized)
    
    paragraph_to_duplicateCount = {}
    duplicates = []
    uniqueParagraphs = set(normalized_paragraphs)

    for p in uniqueParagraphs:
        if p in paragraph_to_duplicateCount:
            continue
        paragraph_to_duplicateCount[p] = -1
        for n in normalized_paragraphs:
            similarity = fuzz.ratio(p, n)
            if similarity >= similarity_threshold:
                paragraph_to_duplicateCount[p] += 1
                duplicates.append([p,n,similarity])
    
    return duplicates, paragraph_to_duplicateCount

def page_contains_dupliacte_paragraphs(htmlContent):
    paragraphs = get_paragraphs(htmlContent)
    print(len(paragraphs))
    duplicates, paragraph_to_duplicateCount = find_duplicates_by_fuzzy(paragraphs, 85)
    print('dups')
    print(len(duplicates))
    print(len(paragraph_to_duplicateCount))

    for x,y in paragraph_to_duplicateCount.items():
        print(x)
        print(y)

    if len(duplicates) == 0:
        print('no duplicates found')
        return False

    #check in avergae the methods have how many duplicates or set any threshold ??
    avg_duplicates = sum(paragraph_to_duplicateCount.values()) / len(paragraph_to_duplicateCount)
    
    print('avg duplicates: '+str(avg_duplicates))
    if avg_duplicates > 2:
        return True
    else:
        return False



print('go go')
# Open the file and read the JSON object
with open('/home/akhatun/Documents/Web-crawler/pages/sample.json', 'r') as file:
    data = json.load(file)
print("is duplicates "+ str(page_contains_dupliacte_paragraphs(data['content'])))
