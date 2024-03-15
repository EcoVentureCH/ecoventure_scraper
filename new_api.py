import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service,
                          options=chrome_options)

def sc_open(url):
    driver.get(url)

def sc_accept_cookies(selenium_by_pair):
    timeout = 3
    try:
        accept_btn = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(selenium_by_pair)
        )
        time.sleep(0.5)
        accept_btn.click()

    except exceptions.ElementNotInteractableException as e:
        print("WARNING: cookies accept thing not Interactable")
    except:
        print("WARNING: no cookie thingi")
        pass

def sc_click_through(selenium_by_pair):
    max_clicks = 10
    timeout = 1

    print('INFO: clicking through: ', end='')
    for i in range(max_clicks):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(selenium_by_pair)
            )
        except:
            break

        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()

        print('.', end=' ')
    print()

def sc_scroll_down(n_pixels = 2000):
    driver.execute_script(f"window.scrollBy(0,{n_pixels})", "");

def sc_get_html():
    html = driver.page_source
    return html

opened_tab = False

def sc_open_tab(url):
    global opened_tab

    if opened_tab:
        print("WARNING: can only have one tab open! closing old one!")
        sc_close_tab()

    driver.execute_script(f'window.open("{url}");')
    driver.switch_to.window(driver.window_handles[1])
    opened_tab = True
    time.sleep(2.5)

def sc_close_tab():
    global opened_tab
    if opened_tab:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        opened_tab = False
    else:
        print("WARNING: cannot close tab, because it was never opened")

def sc_extract_attribute(function_or_regex, html):
    if callable(function_or_regex):
        result = function_or_regex(BeautifulSoup(html, features="html.parser"))
        return result
    result = re.findall(function_or_regex, html)
    if len(result) > 0:
        return result[0]
    print(f"WARNING: regex didn't match html: '{function_or_regex}'")
    return None

def sc_extract_all(data_to_extract: dict, html: str):
    result = {}
    for key, value in data_to_extract.items():
        result[key] = sc_extract_attribute(value, html)
    return result


def number_from_class(bfs, tag, classname, prop = 'class'):
    text = bfs.find_all(tag, {prop: classname})[0].get_text()
    return re.findall(r'\d+[\.\,]?\d*', text)[0]

def text_from_class(bfs, tag, classname, prop = 'class', key = None):

    elem = bfs.find_all(tag, {prop: classname})

    if key == None:
        return elem[0].get_text()
    else:
        return elem[0][key]





def conda():

    # key -> name, value either
    #       -> a function that takes the soup object, and returns the value
    #       -> or a regex
    data_to_extract = {
        'name':           r'<meta\W+property=\"og:title\"\W+content=\"(.*?)\">',
        'external_link':  r'<meta\W+property=\"og:url\"\W+content=\"(.*?)\">',
        'image':          r"<meta\W+property=\"og:image\"\W+content=\"(.*?)\">",
        'min_investment': lambda bfs: number_from_class(bfs, 'p', 'min-investment'),
        'funding_target': lambda bfs: number_from_class(bfs, 'p', 'total-amount'),
    }

    url = 'https://www.conda.ch/projekte-entdecken/'

    sc_open(url)
    sc_accept_cookies((By.ID, 'CookieBoxSaveButton'))
    sc_click_through((By.ID, "campaigns_load_more_btn"))

    html_project_page = sc_get_html()

    regex_projects_urls = r"<a\W+href=\"(https://www\.conda\.ch/.*?)\"\W+target=\".*?class=\".*?\">"
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)

    for url in project_urls:
        sc_open_tab(url)
        html = sc_get_html()

        data = sc_extract_all(data_to_extract, html)
        print(data)

        sc_close_tab()


def seedrs():
    # key -> name, value either
    #       -> a function that takes the soup object, and returns the value
    #       -> or a regex
    data_to_extract = {
        'name':           lambda bfs: text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':  lambda bfs: text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'image':          lambda bfs: text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'min_investment': lambda bfs: number_from_class(bfs, 'tr', 'share-price'),
        'funding_target': lambda bfs: number_from_class(bfs, 'div', 'investment_total_target'),
        'progress':       lambda bfs: number_from_class(bfs, 'div', 'CampaignProgress-text')
    }

    url = 'https://www.seedrs.com/invest/raising-now'

    sc_open(url)

    sc_scroll_down(40000)
    time.sleep(1)

    html_project_page = sc_get_html()

    regex_projects_urls = r'<a href="(/\w+)">'
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)

    for url in project_urls:
        url = 'https://www.seedrs.com' + url
        sc_open_tab(url)
        html = sc_get_html()

        print(f'extracting data from {url}')
        data = sc_extract_all(data_to_extract, html)
        print(data)

        sc_close_tab()



if __name__ == "__main__":
    #conda()
    seedrs()