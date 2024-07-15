import time
import sys
import scraper_definitions as sd 
import src.scraper_api as sc
import src.csv_manager as manager
import requests

from inspect import getmembers, isfunction

time_out_after_job = 7 * 60 # in seconds
csv_filename = "projects.csv"

# first commandline argument is the base path where the data is stored
# if not provided, the base path is where this file is.
if len(sys.argv) > 1:
    base_path = sys.argv[1]
    csv_filename = base_path + "/" + csv_filename

print("Using csv filename:", csv_filename)

scraper_functions = getmembers(sd, isfunction)

with sc.scraper_context(log_out=None, debug=False):
    for name, func in scraper_functions:
        if name[0] == "_":
            continue
        print(f"===Begin scraping function {name}()===")
        project_datas = func()
        print(project_datas)
        print(f"===End scraping function {name}()===")
        if project_datas == None:
            print(f"ERROR: function returned None instead of a dict containing the scraped data.")
            continue
        manager.update_csv(project_datas, csv_filename=csv_filename)

try:
    response = requests.post('http://web:8000/api/reload-projects')
    response.raise_for_status()
    print(f"INFO: reloaded projects successfully: {response.json()}")
except requests.RequestException as e:
    print(f"ERROR: Failed to execute command: {e}")

time.sleep(time_out_after_job)