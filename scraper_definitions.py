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

    to disable: rename `function` to `_function`
    see scraper_api for useful functions (not documented yet!)

'''

import time
import re

from selenium.webdriver.common.by import By

import src.scraper_api as sc
from src.utils import print_flushed as print


def conda():

    # TODO: add projects that have 'starting in ... days'

    data_to_extract = {
        'name':                 r'<meta\W+property=\"og:title\"\W+content=\"(.*?)\">',
        'name_short':           r'<meta\W+property=\"og:title\"\W+content=\"(.*?)\">',
        'external_link':        r'<meta\W+property=\"og:url\"\W+content=\"(.*?)\">',
        'external_image_link':  r"<meta\W+property=\"og:image\"\W+content=\"(.*?)\">",
        'funding_current':      lambda bfs: sc.number_from_class(bfs, 'p', 'min-investment'),
        'funding_min':          r"Mindestinvestition:\W+CHF\W+(.*?)\.-",
        'funding_target':       lambda bfs: sc.number_from_class(bfs, 'p', 'total-amount'),
        'description':          r"<p class=\"text-white large italic text-shadow-dark\">.*?</p>",
        'description_short':    r"<p class=\"text-white large italic text-shadow-dark\">.*?</p>",
        'location':             lambda _: "Switzerland",
    }

    url = 'https://www.conda.ch/projekte-entdecken/'

    sc.open(url)
    sc.accept_cookies((By.ID, 'CookieBoxSaveButton'))
    sc.click_through((By.ID, "campaigns_load_more_btn"))

    html_project_page = sc.get_html()
    regex_projects_urls = r'<a href="(https://www\.conda\.ch/.*?)".*?class="i-btn i-btn-secondary text-uppercase">'

    # TODO(#15): check if all urls are valid!
    # handle error in sc.scrape_projecsts later
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_datas = sc.scrape_projects(data_to_extract, project_urls)

    return project_datas


def seedrs_raising():

    data_to_extract = {
        'name':                lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'name_short':          lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':       lambda bfs: sc.text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'external_image_link': lambda bfs: sc.text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'funding_min':         lambda bfs: sc.number_from_class(bfs, 'span', 'highlights-extra-info'),
        'funding_target':      lambda bfs: sc.number_from_class(bfs, 'div', 'investment_total_target'),
        'funding_current':     lambda bfs: sc.number_from_class(bfs, 'div', 'CampaignProgress-text'),
        'description_short':   lambda bfs: sc.text_from_class(bfs, 'p', 'summary'),
        'description':         lambda bfs: sc.text_from_class(bfs, 'p', 'summary'),
        'location':            lambda bfs: sc.text_from_class(bfs, 'tr', 'location').replace("\n", " "),
    }

    url = 'https://www.seedrs.com/invest/raising-now'

    sc.open(url)
    for i in range(10):
        sc.scroll_down(400)
        time.sleep(1)
    

    #regex_projects_urls = r'<a href="(/\w+)">'
    regex_projects_urls = r'<a href=\"(/[a-zA-Z\-\d\_]+?)\">'
    html_project_page = sc.get_html()
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_urls = ['https://www.seedrs.com' + url for url in project_urls]

    project_datas = sc.scrape_projects(data_to_extract, project_urls)
    print("seedrs test end")
    
    return project_datas

if __name__ == "__main__":
    with sc.scraper_context(debug=True):
        conda()
        seedrs_raising()
