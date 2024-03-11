'''
test scraper for scraping active projects on www.conda.ch
'''
import sys
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions
import pandas as pd
from src.utils import print_flushed as print


URL = 'https://www.conda.ch/projekte-entdecken/'
CSV_FNAME = 'projects.csv'
ATTRIBUTE_TIMEOUT = 3

# attr_name : (css selector, html attribute | re.comile('..'))
# regex tries to findall in innerHTML
ATTRIBUTE_CSS_SELECTORS = {
    'external_link' : ('meta[property="og:url"]', 'content'),
    'name': ('meta[property="og:title"]', 'content') ,
    'image': ('meta[property="og:image"]', 'content'),
    'min_investment': ('p.min-investment', re.compile(r'(?:\d*\.)?\d+')),
}

UPDATABLE = list(ATTRIBUTE_CSS_SELECTORS.keys())
UPDATABLE.remove('external_link')

def update_csv(project_list):
    print(f'INFO: writing entries to {CSV_FNAME}')
    
    if os.path.exists(CSV_FNAME):
        df = pd.read_csv(CSV_FNAME)
    else:
        df = pd.DataFrame()
        for attributes in project_list:
            df = pd.concat([df, pd.DataFrame([attributes])], ignore_index=True)

    links = df['external_link']
    for attributes in project_list:
        if attributes['external_link'] in links.values:
            # update attributes
            rows = df.loc[df['external_link'] == attributes['external_link']]
            assert(len(rows)==1)
            for key in UPDATABLE:
                df.loc[df['external_link'] == attributes['external_link'], key] = attributes[key]
        else:
            df = pd.concat([df, pd.DataFrame([attributes])], ignore_index=True)

    df.to_csv(CSV_FNAME, index=False)    

def read_projects_conda(driver, url=URL):
    driver.get(url)
    # accept cookies
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'CookieBoxSaveButton'))
        ).click()
    except exceptions.ElementNotInteractableException as e:
        print("WARNING: cookies accept thing not Interactable")


    # click through load next page.    
    while True:
        try:
            element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "campaigns_load_more_btn"))
            )
        except:
            break
        driver.execute_script("arguments[0].scrollIntoView();", element)

        element.click()
        print('.', end='')
    print()


    campaign_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'campaign-load-me'))
    )


    project_list = []
    for elem in campaign_elements:
        buttons = elem.find_elements(By.CLASS_NAME, 'i-btn')
        buttons_green = elem.find_elements(By.CSS_SELECTOR, 'a.i-btn:not(.i-btn-gray)')
        assert (len(buttons) == 1)
        if len(buttons_green) == 1:
            campaing_url = buttons_green[0].get_attribute('href')
            driver.execute_script(f'window.open("{campaing_url}");')
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(1.5)

            attributes = {}
            # take attributes
            for attribute_name, (selector, html_attr_or_regex) in ATTRIBUTE_CSS_SELECTORS.items():
                value = ''
                try:
                    meta_tag = WebDriverWait(driver, ATTRIBUTE_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )

                    if isinstance(html_attr_or_regex, str): 
                        value = meta_tag.get_attribute(html_attr_or_regex)
                    else:
                        innnerHTML = meta_tag.get_attribute('innerHTML')
                        regex_result = html_attr_or_regex.findall(innnerHTML)
                        if len(regex_result) > 0:
                            value = regex_result[0]
                except exceptions.TimeoutException as e:
                    print(f'WARNING: didn\'t find attribute {attribute_name} on page {campaing_url} waiting for {ATTRIBUTE_TIMEOUT} seconds')
                    continue

                attributes[attribute_name] = value
            
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            project_list.append(attributes)
    
    print(f"INFO: projcet_list has {len(project_list)} entries")
    update_csv(project_list)


class scraper_start:
    '''class that handles wendriver close in a context
    
       example:
       
       with scraper_start() as scraper:
           scraper.run()
    '''
    def __init__(self, log_out=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.crome_options = chrome_options
        self.log_out = log_out
        
    def __enter__(self):
        if self.log_out is not None:
            print(f'INFO: all stdout will be printed to {self.log_out}')
            sys.stdout.flush()
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            sys.stdout = open(self.log_out, 'w')
            sys.stderr = sys.stdout

        print('INFO: starting chrome driver')
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, 
                                       options=self.crome_options)
        print('INFO: started chrome driver')
        return self
        
    def __exit__(self, *args):
        if self.log_out is not None:
            sys.stdout.close()
            sys.stdout = self._stdout
            sys.stderr = self._stderr
            sys.stdout.flush()
            sys.stderr.flush()

        print('INFO: exiting scraper_start()')
        self.driver.quit()
        print('INFO: exited scraper_start()')



    def run(self):
        read_projects_conda(self.driver)

if __name__ == "__main__":
    with scraper_start() as scraper:
        scraper.run()
