import requests
import cbor
import time
from threading import RLock
import time
import datetime

from utils.response import Response
from utils import ThreadShelf, domain_extractor

lock = RLock()

def download(url, config, logger=None):
    host, port = config.cache_server
    stash = ThreadShelf("lockme.shelve")
    end_domain = domain_extractor(url)
    h_ed = "lock_" + end_domain
    print(h_ed, end_domain)
    while True:
        flag = False
        with lock:
            if h_ed not in stash:
                stash[h_ed] = 0
            if end_domain not in stash:
                stash[end_domain] = datetime.datetime(1970,1,3).isoformat()
            val = stash[h_ed]
            if val == 0:
                stash[h_ed] = 1
                flag = True
        if flag:
            time.sleep(max(0, (datetime.datetime.fromisoformat(stash[end_domain]) - datetime.datetime.now() + datetime.timedelta(seconds=0.5)).total_seconds()))
            break
        else:
            time.sleep(0.1)
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", f"{url}"), ("u", f"{config.user_agent}")])
    with lock:
        stash[h_ed] = 0
        stash[end_domain] = datetime.datetime.now().isoformat()
    try:
        if resp and resp.content:
            return Response(cbor.loads(resp.content))
    except (EOFError, ValueError) as e:
        pass
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
