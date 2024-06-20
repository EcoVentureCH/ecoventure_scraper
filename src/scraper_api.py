'''
  scraper API for defining project scrapers

  TODO(#17): document scraper_api!
'''

import re
import time
import sys

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils import log_c, log


# global state
driver = None
opened_tab = False

class scraper_context:
    '''class that handles wendriver close in a context

       example:

       with scraper_context():
           pass
    '''
    def __init__(self, log_out=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--output=/dev/null")
        self.crome_options = chrome_options
        self.log_out = log_out

    def __enter__(self):
        global driver
        if self.log_out is not None:
            log_c(f'INFO: entered scraper_context - all stdout will now be printed to {self.log_out}')
            sys.stdout.flush()
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            sys.stdout = _open(self.log_out, 'w')
            sys.stderr = sys.stdout

        self.service = Service(ChromeDriverManager().install(), log_output='chrome_log.txt')
        self.driver = webdriver.Chrome(service=self.service,
                                       options=self.crome_options)
        log('INFO: started chrome driver')
        driver = self.driver
        return self

    def __exit__(self, *args):
        if self.log_out is not None:
            sys.stdout.close()
            sys.stdout = self._stdout
            sys.stderr = self._stderr
            sys.stdout.flush()
            sys.stderr.flush()

        self.driver.quit()
        log('INFO: exited scraper_context!')

_open = open

def open(url):
    driver.get(url)

def accept_cookies(selenium_by_pair):
    timeout = 3
    try:
        accept_btn = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(selenium_by_pair)
        )
        time.sleep(0.5)
        accept_btn.click()

    except exceptions.ElementNotInteractableException as e:
        log("WARNING: cookies accept thing not Interactable")
    except:
        log("WARNING: no cookie thingi")
        pass

def click_through(selenium_by_pair):
    max_clicks = 10
    timeout = 1

    log('INFO: clicking through: ', end='')
    for i in range(max_clicks):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(selenium_by_pair)
            )
        except:
            break

        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()

        log('.', end=' ')
    log()

def scroll_down(n_pixels = 2000):
    driver.execute_script(f"window.scrollBy(0,{n_pixels})", "");

def get_html():
    html = driver.page_source
    return html

def open_tab(url):
    global opened_tab

    if opened_tab:
        log("WARNING: can only have one tab open! closing old one!")
        close_tab()

    driver.execute_script('window.open(arguments[0], "_blank");', url)
    driver.switch_to.window(driver.window_handles[1])
    opened_tab = True
    time.sleep(2.5)

def close_tab():
    global opened_tab
    if opened_tab:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        opened_tab = False
    else:
        log("WARNING: cannot close tab, because it was never opened")

def extract_attribute(function_or_regex, html):
    if callable(function_or_regex):
        result = function_or_regex(BeautifulSoup(html, features="html.parser"))
        return result
    result = re.findall(function_or_regex, html)
    if len(result) > 0:
        return result[0]
    log(f"WARNING: regex didn't match html: '{function_or_regex}'")
    return None

# data_to_extract:
#    key   -> name
#    value -> either a function that takes the soup object and returns the value
#             or     a regex that extracts a specific text

def extract_all(data_to_extract: dict, html: str):
    result = {}
    for key, value in data_to_extract.items():
        result[key] = extract_attribute(value, html)
    return result

def scrape_projects(data_to_extract, project_urls):
    log(f'INFO: got {len(project_urls)} projects.')

    project_datas = []
    for i, url in enumerate(project_urls):
        open_tab(url)
        html = get_html()
        data = extract_all(data_to_extract, html)
        project_datas.append(data)
        log(f'INFO: extracted project {i+1}/{len(project_urls)}.')
        close_tab()

    return project_datas


def number_from_class(bfs, tag, classname, prop = 'class'):
    found = bfs.find_all(tag, {prop: classname})

    if len(found) < 1:
        log("WARNING: didn't find {},{},{}".format(tag, classname, prop))
        return None

    text = found[0].get_text()
    matches = re.findall(r'\d+[\.\,]?\d*', text)

    if len(matches) > 0:
        return matches[0]
    log("WARNING: didn't match any number in {},{},{}".format(tag, classname, prop))
    return None

def text_from_class(bfs, tag, classname, prop = 'class', key = None):
    elem = bfs.find_all(tag, {prop: classname})
    if key == None:
        return elem[0].get_text()
    return elem[0][key]
