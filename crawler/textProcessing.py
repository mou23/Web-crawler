from collections import Counter
import numpy as np
import hashlib as hf
import json
from bs4 import BeautifulSoup
import os


#basic simhash algorithm
def md5HashToBinary(token,bitSize):
    md5Hash = hf.md5()
    md5Hash.update(token.encode('utf-8'))
    binaryToken = bin(int(md5Hash.hexdigest(), 16))[2:].zfill(bitSize)
    return binaryToken


def fingerPrint(tokens, bitSize):
    tokensWithFrequency = Counter(tokens)
    weightedBitVector = np.zeros(bitSize, dtype=int)

    for token, count in tokensWithFrequency.items():
        tokenBitVector = md5HashToBinary(token,bitSize)

        for i in range(bitSize):
            if tokenBitVector[i] == '1':
                weightedBitVector[i] = weightedBitVector[i]+count
            else:
                weightedBitVector[i]= weightedBitVector[i]-count
    
    simhash = ''
    for i in range(bitSize):
        if weightedBitVector[i] >= 0:
            simhash = simhash+'1'
        else:
            simhash = simhash+'0'

    return simhash

def getHammingDistance(fingerPrint1, fingerPrint2, bitSize):
    distance = 0
    for i in range(bitSize):
        if fingerPrint1[i] != fingerPrint2[i]:
            distance = distance + 1
    return distance
    
def simhashSimilarity(docOnetokens, docTwoTokens):
    bitSize = 128
    docOneFingerPrint = fingerPrint(docOnetokens, bitSize)
    docTwoFingerPrint = fingerPrint(docTwoTokens, bitSize)
    hammingDistance = getHammingDistance(docOneFingerPrint, docTwoFingerPrint, bitSize)
    similarity = 1 - (hammingDistance / len(docOneFingerPrint))
    return similarity

#removes non-text tags
def getTextContentOnly(htmlContent):
    soup = BeautifulSoup(htmlContent, 'html.parser')
    tags_to_remove = ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'svg', 'canvas']
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()  # Remove the tag from the tree

    # Return the cleaned HTML as a string
    text_content = soup.get_text(separator=' ', strip=True)
    return text_content



def readCrawledDocuments():
    ## needs to updated for new crawled document
    with open('pages/344eba531529982e8a935c573a8837f4dbca46fb8bc1c9aacbe8db323864aa6d.json', 'r') as file:
        obj = json.load(file)
        baseHtmlContent = obj.get("content")
        baseTextOnlyHtmlContent = getTextContentOnly(baseHtmlContent)

    for _, _, files in os.walk('pages/'):
        for filename in files:
            with open(os.path.join('pages/', filename), 'r') as file:
                obj = json.load(file)
                htmlContent = obj.get("content")
                textOnlyHtmlContent = getTextContentOnly(htmlContent)
                sim = simhashSimilarity(baseTextOnlyHtmlContent, textOnlyHtmlContent)
                #print(textOnlyHtmlContent)
                print(sim)
            


readCrawledDocuments()