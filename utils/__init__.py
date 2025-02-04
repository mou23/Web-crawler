import os
import logging
from hashlib import sha256
from urllib.parse import urlparse
import sqlite3
import json

def get_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
       "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_urlhash(url):
    parsed = urlparse(url)
    # everything other than scheme.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}/{parsed.fragment}".encode("utf-8")).hexdigest()

def normalize(url):
    if url.endswith("/"):
        return url.rstrip("/")
    return url

def domain_extractor(dom: str) -> str:
    return urlparse(dom).netloc

# SQLite3 supports multithreading safely
class ThreadShelf:
    def __init__(self, path: str):
        self.path = path
        conn = sqlite3.connect(self.path, check_same_thread=False)
        curr = conn.cursor()
        curr.execute("CREATE TABLE IF NOT EXISTS store ( "
                     "  k TEXT PRIMARY KEY,"
                     "  v TEXT"
                     ");")
        conn.commit()
        curr.close()
        conn.close()
    def __getitem__(self, k: str):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        curr = conn.cursor()
        curr.execute("SELECT v "
                     "FROM store "
                     "WHERE k = ?;", (k,))
        r = curr.fetchall()
        curr.close()
        conn.close()
        if len(r) != 1:
            raise KeyError(k)
        ld = json.loads(r[0][0])
        if type(ld) is list:
            return tuple(ld)
        else:
            return ld
    def __setitem__(self, k: str, v):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        curr = conn.cursor()
        nv = json.dumps(v)
        curr.execute("INSERT INTO store (k, v) "
                     "VALUES (?, ?) "
                     "ON CONFLICT(k) DO UPDATE SET v = ?;", (k, nv, nv))
        curr.close()
        conn.commit()
        conn.close()
    def __contains__(self, k: str):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        curr = conn.cursor()
        curr.execute("SELECT 1 "
                     "FROM store "
                     "WHERE k = ?;", (k,))
        r = curr.fetchall()
        curr.close()
        conn.close()
        return len(r) == 1
    def sync(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.commit()
        conn.close()
