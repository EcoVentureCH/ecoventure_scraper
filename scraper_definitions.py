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
import logging

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
        #'funding_current':      lambda bfs: sc.currency_comma_means_dot(bfs, 'p', 'min-investment'),
        'funding_current':      r"<p class=\"conda-knob-value-text\".*?>.*?(\d+[\.\,]?\d*)\W+CHF</p>",
        'funding_min':          r"Mindestinvestition:\W+CHF\W+(\d*?)\.[\-\d]",
        'funding_target':       lambda bfs: sc.currency_comma_means_dot(bfs, 'p', 'total-amount'),
        'description':          r"<p class=\"text-white large italic text-shadow-dark\">(.*?)</p>",
        'description_short':    r"<p class=\"text-white large italic text-shadow-dark\">(.*?)</p>",
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

    # set location and currency for all projects
    for i in range(len(project_datas)):
        project_datas[i]['location'] = "Switzerland"
        project_datas[i]['currency'] = "CHF"
        # THe , and . usage is so confusing on conda.ch....
        project_datas[i]['funding_current'] = project_datas[i]['funding_current'].replace(".", "")

    return project_datas

'''

def seedrs_raising():

    data_to_extract = {
        'name':                lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'name_short':          lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':       lambda bfs: sc.text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'external_image_link': lambda bfs: sc.text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'funding_min':         lambda bfs: sc.currency_dot_means_dot(bfs, 'span', 'highlights-extra-info'),
        'funding_target':      lambda bfs: sc.currency_dot_means_dot(bfs, 'div', 'investment_total_target'),
        'funding_current':     lambda bfs: sc.currency_dot_means_dot(bfs, 'div', 'CampaignProgress-text'),
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

    # set currency to GBP for all projects
    # TODO: replace with scraping the currency - should not be very difficult...
    for i in range(len(project_datas)):
        project_datas[i]['currency'] = "GBP"

    return project_datas
    
    
    

def econeers():
    def text_from_class(bfs, tag, class_name):
        try:
            element = bfs.find(tag, class_=class_name)
            if element:
                return element.get_text(strip=True)
            else:
                print('element not found')
                return None
            
        except AttributeError:
            return None

    def text_from_meta(bfs, tag, attr, value, key='content'):
        print(bfs.find_all(tag, {attr: value}))
        try:
            return bfs.find_all(tag, {attr: value})
        except (AttributeError, TypeError):
            print("Error finding text from meta")
            return None

    def number_from_class(bfs, tag, class_name):
        try:
            text = bfs.find_all(tag, class_=class_name).get_text(strip=True)
            return int(re.sub(r'[^\d]', '', text))
        except (AttributeError, ValueError):
            print("Error finding number from class")
            return None
        
 

    data_to_extract = {
        #'name': lambda bfs: sc.text_from_class(bfs, 'meta',   'og:description', 'property', key='content'),
        'external_link':  lambda bfs: sc.text_from_class(bfs, 'meta',  'og:url', 'property', key='content'),
        'image':  lambda bfs: sc.text_from_class(bfs, 'meta',   'og:image', 'property', key='content'),
        'min_investment': lambda bfs: number_from_class(bfs, 'td', 'tg-kftd'),
        'funding_target': lambda bfs: number_from_class(bfs, 'td', 'tg-lqy6'),
        'progress': lambda bfs: number_from_class(bfs, 'h2', 'center-text')
    }
    
    print('econeers start')
    url = 'https://www.econeers.de/#aktuelle-investmentchancen'
    
    sc.open(url)

    html_project_page = sc.get_html()
    regex_projects_urls = r'<a (href="https:\/\/www.econeers.de\/investmentchancen\/.*?)"'
    
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_urls = ['https://www.econeers.de' + url for url in project_urls]
    
    print("data to extract")
    print(data_to_extract)
    print("project urls")
    print(project_urls)
    
    project_datas = sc.scrape_projects(data_to_extract, project_urls)
    
    print("econeers end")
    
    return project_datas

if __name__ == "__main__":
    with sc.scraper_context(debug=False):
        print(conda())
        print(seedrs_raising())
