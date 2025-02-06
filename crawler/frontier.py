import os
import shelve

import threading 
from queue import PriorityQueue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

from collections import defaultdict
from urllib.parse import urlparse
import time
from utils.domain import _get_three_level_domain

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = PriorityQueue()

        self.lock = threading.Lock()
        self.domain_locks  = defaultdict(threading.Lock)
        self.last_crawl_time = defaultdict(int)
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.put(TimedTask(time.time(), url))
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)

        with self.lock:
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                self.to_be_downloaded.put(TimedTask(time.time(), url))
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        with self.lock:
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = (url, True)
            self.save.sync()

    def get_domain_lock(self, url):
        domain = urlparse(url).netloc
        if domain not in self.domain_locks:
            self.domain_locks[domain] = threading.Lock()
        return self.domain_locks[domain]
    
    def get_tbd_url(self):
        if self.queue_is_empty(self.to_be_downloaded):
            return None
        
        with self.lock:
            while True:
                url = self.to_be_downloaded.get().url
                domain = _get_three_level_domain(url)
                domain_lock = self.get_domain_lock(url)

                with domain_lock:
                    elapsed_time_since_last_crawl = time.time() - self.last_crawl_time[domain]
                    if elapsed_time_since_last_crawl < self.config.time_delay:
                        self.to_be_downloaded.put(TimedTask(time.time() + 1, url)) # put back to queue
                    else:
                        self.last_crawl_time[domain] = time.time()
                        return url
    
    def queue_is_empty(self, q, timeout=5):
        if q.empty():
            time.sleep(timeout)
            return q.empty() 
        return False 
    
class TimedTask:
    def __init__(self, timestamp, url):
        self.timestamp = timestamp
        self.url = url

    def __lt__(self, other):
        return self.timestamp < other.timestamp