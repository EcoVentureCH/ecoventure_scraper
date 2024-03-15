import multiprocessing
import signal
import sys
import time
import os

from src.utils import print_with_color as print_c

import src.scraper_api as sc

from src.csv_manager import update_csv

from src.wc_projects import update_projects
from src.wc_images import upload_images


from inspect import getmembers, isfunction


WEBSITE = "https://www.ecoventure.ch"
LOG_FILE = "log.txt"
DAEMON_STATE_FILE = ".daemon_state"

def soft_exit(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, soft_exit)

def scrape_and_upload(seconds):
    print_c('INFO: running scrape_and_upload() function')

    import scraper_definitions as sd
    scraper_functions = getmembers(sd, isfunction)

    with sc.scraper_context(log_out=LOG_FILE):
        print("INFO: started webdriver")
        while True:
            
            start_time = time.time()

            # run scrapers
            for name, func in scraper_functions:
                print(f"INFO: running scraper named `{name}`. ")
                project_datas = func()
                update_csv(project_datas)

            return_code = 1
            duration = time.time() - start_time
            print(f'INFO: scraper finished in {duration} seconds')
            print()

            start_time_upload = time.time()

            try:
                print("INFO: start udpating projectss")
                update_projects()
                print("INFO: start uploading images")
                upload_images()

            except FileNotFoundError as e:
                print(e)
                print(f"WARNING: couldn't upload to {WEBSITE}")

            else:
                duration = time.time() - start_time_upload
                print(f"INFO: uploaded changes to {WEBSITE} took {duration} sec")

            duration = time.time() - start_time
            remaining_sleep_timer = max(seconds - duration, 0)

            print(f'INFO: next scrape job in {remaining_sleep_timer/60:.1f} min')
            print()

            time.sleep(remaining_sleep_timer)


def detached(*args):
    pid =  os.fork()
    if pid != 0:
        print_c(f"INFO: daemon started with PID: {pid}")
        with open(DAEMON_STATE_FILE, "w") as f:
            f.write(str(pid))
        return

    scrape_and_upload(*args)

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

def get_pid():

    def check_pid(pid):        
        """ Check For the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True
        
    if os.path.exists(DAEMON_STATE_FILE):
        with open(DAEMON_STATE_FILE, 'r') as f:
            pid = int(f.read())
        if check_pid(pid):
            return pid
    return -1


if __name__ == "__main__":
    restart_daemon(30)
    time.sleep(100)
    stop_daemon()
