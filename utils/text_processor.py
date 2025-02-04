from bs4 import BeautifulSoup

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


def get_similar_paragraphs_in_single_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')  
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.get_text(strip='True'))