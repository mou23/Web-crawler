import numpy as np
import hashlib as hf
from rocksdict import Rdict
from collections import Counter

def hash_to_binary(token,bit_size):
    md5_hash = hf.md5()
    md5_hash.update(token.encode('utf-8'))
    binary_token = bin(int(md5_hash.hexdigest(), 16))[2:].zfill(bit_size)
    return binary_token


def get_finger_print(tokens, bit_size = 128):
    tokens_with_frequency = Counter(tokens)
    weighted_bit_vector = np.zeros(bit_size, dtype=int)

    for token, count in tokens_with_frequency.items():
        token_bit_vector = hash_to_binary(token,bit_size)

        for i in range(bit_size):
            if token_bit_vector[i] == '1':
                weighted_bit_vector[i] = weighted_bit_vector[i]+count
            else:
                weighted_bit_vector[i]= weighted_bit_vector[i]-count
    
    simhash = ''
    for i in range(bit_size):
        if weighted_bit_vector[i] >= 0:
            simhash = simhash+'1'
        else:
            simhash = simhash+'0'

    return simhash


def get_hamming_distance(fingerPrint1, fingerPrint2, bit_size = 128):
    distance = 0
    for i in range(bit_size):
        if fingerPrint1[i] != fingerPrint2[i]:
            distance = distance + 1
    return distance
 

def get_cosine_similarity(fingerprint1, fingerprint2):
    a = np.array([int(bit) for bit in fingerprint1])
    b = np.array([int(bit) for bit in fingerprint2])
    
    dot_product = np.dot(a, b)
    magnitude_a = np.linalg.norm(a)
    magnitude_b = np.linalg.norm(b)
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0
    
    return dot_product / (magnitude_a * magnitude_b)


def get_simhash_similarity(fingerprint1, fingerprint2):
    hamming_distance = get_hamming_distance(fingerprint1, fingerprint2)
    similarity = 1 - (hamming_distance / len(fingerprint1))
    # cosine_similarity = get_cosine_similarity(fingerprint1, fingerprint2)
    # print("cosine sim is"+ str(cosine_similarity))
    return similarity


def similar_content_exist(url, new_content):
    db = Rdict("./fingerprints")
    new_finger_print = get_finger_print(new_content)
    
    found_similar_content = False
    for current_url, current_fingerprint in db.items():
        similarity = get_simhash_similarity(new_finger_print, current_fingerprint)
        if similarity >= 0.97:
            print(f"{url} matched with URL: {current_url}")
            found_similar_content = True
            break
    
    if found_similar_content == False:
        db[url] = new_finger_print
    
    db.close()

    return found_similar_content