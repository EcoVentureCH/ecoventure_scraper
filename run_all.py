import time
import scraper_definitions as sd 
import src.scraper_api as sc
from inspect import getmembers, isfunction

scraper_functions = getmembers(sd, isfunction)

with sc.scraper_context(log_out=None):
    for name, func in scraper_functions:
        print(f"===Begin scraping function {name}()===")
        project_datas = func()
        print(project_datas)
        print(f"===End scraping function {name}()===")

time.sleep(100000)