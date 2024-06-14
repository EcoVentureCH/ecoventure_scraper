import time
import sys
import scraper_definitions as sd 
import src.scraper_api as sc
import src.csv_manager as manager

from inspect import getmembers, isfunction

csv_filename = "projects.csv"

if len(sys.argv) > 1:
    # (most likely) used to call from docker
    volume = sys.argv[1]
    print("Volume to scrape stuff to is: ", volume)
    csv_filename = volume + "/" + csv_filename

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

#time.sleep(100000)