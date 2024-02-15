import multiprocessing
import signal
import sys
import time
import os

from src.utils import print_with_color as print_c
from src.scraper_conda_ch import URL, scraper_start
from src.updateProducts import update_products
from src.uploadProducts import upload_products, WEBSITE
from src.uploadImage import upload_images

DAEMON_STATE_FILE = ".daemon_state"
LOG_FILE = "log.txt"

def soft_exit(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, soft_exit)

def scrape_and_upload(seconds):

    print_c('INFO: running scrape_and_upload() function')
    with scraper_start(log_out=LOG_FILE) as scraper:

        print_c("INFO: started webdriver")
        while True:
            print_c(f"INFO: scraping '{URL}' ")
            
            start_time = time.time()
            scraper.run()
            return_code = 1
            duration = time.time() - start_time
            print_c(f'INFO: scraper finished in {duration} seconds')
            print()

            start_time_upload = time.time()

            try:
                print_c("INFO: start udpating products")
                update_products()
                print_c("INFO: start uploading images")
                upload_images()
                print_c("INFO: start uploading projects")
                upload_products()
            except FileNotFoundError as e:
                print(e)
                print_c(f"WARNING: couldn't upload to {WEBSITE}")
            else:
                duration = time.time() - start_time_upload
                print_c(f"INFO: uploaded changes to {WEBSITE} took {duration} sec")

            duration = time.time() - start_time
            remaining_sleep_timer = max(seconds - duration, 0)

            print_c(f'INFO: next scrape job in {remaining_sleep_timer/60} min')
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
    time.sleep(2.2)
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
    restart_daemon(30)
    time.sleep(100)
    stop_daemon()