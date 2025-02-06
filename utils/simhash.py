import threading
from rocksdict import Rdict
from utils.similar_content_checker import get_finger_print, get_simhash_similarity

class SimhashDBManager:
    _shared_state = {}  # Borg shared state
    _lock = threading.Lock()

    def __init__(self, db_path="./fingerprints"):
        self.__dict__ = self._shared_state
        if not hasattr(self, "initialized"):
            with self._lock:
                if not hasattr(self, "initialized"):
                    self._init_db(db_path)
                    self.initialized = True

    def _init_db(self, db_path):
        self.db_path = db_path
        self.db = Rdict(self.db_path)
        self.db_lock = threading.Lock()
        self.counter = 0

    def close(self):
        self.db.close()

    def is_duplicate(self, url, new_content):
        new_finger_print = get_finger_print(new_content)
        
        with self.db_lock: 
            for current_url, current_fingerprint in self.db.items():
                similarity = get_simhash_similarity(new_finger_print, current_fingerprint)
                if similarity >= 0.99:
                    print(f"{url} matched with URL: {current_url}, {similarity}")
                    return True

            self.db[url] = new_finger_print
            self.counter += 1

            if self.counter % 1000 == 0:
                self.flush_db()
            
        return False

    def flush_db(self):
        self.db.close()
        self.db = Rdict(self.db_path)