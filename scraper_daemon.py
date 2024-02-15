import multiprocessing
import signal
import sys
import time
import os
from utils import print_with_color as print_c

from scraper_conda_ch import URL, run_scraper


def scrape_and_upload(seconds):

    print_c('INFO: running scrape_and_upload()')

    while True:
        print_c(f"INFO: scraping '{URL}' ")
        
        return_code = 0
        start_time = time.time()
        try:
            run_scraper()
        except Exception as e:
            print(e)
            print_c('WARNING: got errors in run_scraper()')
            return_code = 1

        duration = time.time() - start_time

        if return_code == 0:
            print_c(f'INFO: scraper finished in {duration} seconds')
        print()

        # TODO: add uppload functionality here


        duration = time.time() - start_time
        remaining_sleep_timer = max(seconds - duration, 0)
        time.sleep(remaining_sleep_timer)

DAEMON_STATE_FILE = ".daemon_state"
LOG_FILE = "log.txt"

def detached(*args):
    pid =  os.fork()
    if pid != 0:
        print_c(f"INFO: daemon started with PID: {pid}")
        with open(DAEMON_STATE_FILE, "w") as f:
            f.write(str(pid))
        return

    stdout = sys.stdout
    with open(LOG_FILE, 'w') as sys.stdout:
        scrape_and_upload(*args)
    sys.stdout = stdout

def restart_daemon(seconds=1):
    stop_daemon()
    process = multiprocessing.Process(target=detached,
                                       args=(seconds,),)
    process.daemon = True
    process.start()
    process.join()

def stop_daemon():
    if not os.path.exists(DAEMON_STATE_FILE):
        print_c(f"INFO: daeomon not running")
        return
    
    with open(DAEMON_STATE_FILE, 'r') as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        print_c(f"INFO: killed daemon with PID: {pid}")
    except ProcessLookupError:
        print_c(f"INFO: did not find daemon with PID: {pid}")
        pass

    os.remove(DAEMON_STATE_FILE)

if __name__ == "__main__":
    restart_daemon()
    time.sleep(10)
    kill_daemon_silent()