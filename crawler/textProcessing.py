from collections import Counter
import numpy as np
import hashlib as hf
#basic simhash algorithm
def md5HashToBinary(token):
    md5Hash = hf.md5()
    md5Hash.update(token.encode('utf-8'))
    binaryToken = bin(int(md5Hash.hexdigest(), 16))[2:].zfill(8)
    return binaryToken

def simhashSimilarity(docOnetokens, docTwoTokens, bitSize):
    docOneFingerPrint = fingerPrint(docOnetokens, 8)

def fingerPrint(tokens, bitSize):
    tokensWithFrequency = Counter(tokens)
    weightedBitVector = np.zeros(bitSize, dtype=int)
    for token, count in tokensWithFrequency.items():
        tokenBitVector = md5HashToBinary(token)

        for i in range(bitSize):
            weightedBitVector[i] += (2 * (tokenBitVector[i] - 0.5)) * count  # weight by frequency
    
    simhash = 0
    for i in range(bitSize):
        if weightedBitVector[i] > 0:
            simhash |= (1 << i)  # set the i-th bit to 1 if positive

    return simhash

    


