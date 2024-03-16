'''
scraper definitions:

    define functions in this file that:
        - takes no arguments
        - return a list of dictionaries for each project
          with entries for each project like:

            [{ 'name': 'project 1',
                ... },
             { 'name': 'project 2'
                ... },
            ...
            ]

    each function in this file is imported by the scraper_daemon
    and executed regularly.

    to disable: rename `function` to `_function`

    see scraper_api for useful functions (not documented yet!)
'''

import time
import re

from selenium.webdriver.common.by import By

import src.scraper_api as sc
from src.utils import print_flushed as print


def conda():

    data_to_extract = {
        'name':           r'<meta\W+property=\"og:title\"\W+content=\"(.*?)\">',
        'external_link':  r'<meta\W+property=\"og:url\"\W+content=\"(.*?)\">',
        'image':          r"<meta\W+property=\"og:image\"\W+content=\"(.*?)\">",
        'min_investment': lambda bfs: sc.number_from_class(bfs, 'p', 'min-investment'),
        'funding_target': lambda bfs: sc.number_from_class(bfs, 'p', 'total-amount'),
    }

    url = 'https://www.conda.ch/projekte-entdecken/'

    sc.open(url)
    sc.accept_cookies((By.ID, 'CookieBoxSaveButton'))
    sc.click_through((By.ID, "campaigns_load_more_btn"))

    html_project_page = sc.get_html()
    regex_projects_urls = r'<a href="(https://www\.conda\.ch/.*?)".*?class="i-btn i-btn-secondary text-uppercase">'

    # TODO: check if all urls are valid!
    # handle error in sc.scrape_projecsts later
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_datas = sc.scrape_projects(data_to_extract, project_urls)

    return project_datas


def seedrs():

    data_to_extract = {
        'name':           lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':  lambda bfs: sc.text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'image':          lambda bfs: sc.text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'min_investment': lambda bfs: sc.number_from_class(bfs, 'tr', 'share-price'),
        'funding_target': lambda bfs: sc.number_from_class(bfs, 'div', 'investment_total_target'),
        'progress':       lambda bfs: sc.number_from_class(bfs, 'div', 'CampaignProgress-text')
    }

    url = 'https://www.seedrs.com/invest/raising-now'

    sc.open(url)
    sc.scroll_down(40000)
    time.sleep(1)

    html_project_page = sc.get_html()

    regex_projects_urls = r'<a href="(/\w+)">'
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_urls = ['https://www.seedrs.com' + url for url in project_urls]

    project_datas = sc.scrape_projects(data_to_extract, project_urls)

    return project_datas


if __name__ == "__main__":
    with sc.scraper_context():
        conda()
        seedrs()