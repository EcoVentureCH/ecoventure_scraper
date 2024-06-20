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
import logging

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

    # TODO(#15): check if all urls are valid!
    # handle error in sc.scrape_projecsts later
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_datas = sc.scrape_projects(data_to_extract, project_urls)

    return project_datas

'''

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
    
    
    print("seedrs test start")
 #   print(html_project_page)
    
    

    regex_projects_urls = r'<a href="(/\w+)">'
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_urls = ['https://www.seedrs.com' + url for url in project_urls]

    project_datas = sc.scrape_projects(data_to_extract, project_urls)
    print("seedrs test end")
    
    
    return project_datas

'''
def republic():
    data_to_extract = {
        'name':           lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':  lambda bfs: sc.text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'image':          lambda bfs: sc.text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'min_investment': lambda bfs: sc.number_from_class(bfs, 'div', 's-marginTop0_5 u-textCenter s-fontSize14 u-fontWeight400 u-colorMuted'),
        'funding_target': lambda bfs: sc.number_from_class(bfs, 'div', 'u-fontWeight600 u-textRight s-marginLeft1 offerings-show-flexible_deal_terms-item__value'),
        'progress':       lambda bfs: sc.number_from_class(bfs, 'div', 's-marginBottom1_5 s-borderBottom1_5 offerings-show-header-raised_amount')
    }
    
    print('republic test start')
    
    url = 'https://republic.com/companies'
    
    sc.open(url)
    
    
    sc.scroll_down(40000)
    time.sleep(1)
    sc.scroll_down(40000)
    time.sleep(1)
    
    
    html_project_page = sc.get_html()
    time.sleep(1)
    
    html_project_page = sc.get_html()
    
    #print(html_project_page)
    regex_projects_urls = r'<a href=\"(.+)\" itemscope>'
     #r'<p\s+class=["\']OfferingCardContent-module__title___DrRba["\']\s+itemProp=["\']name["\']>([^<]+)<\/p>' #r'<a href=\"(.+)\" itemscope>'
    
    print('Number of projects:' + str(len(re.findall(regex_projects_urls, html_project_page, re.MULTILINE))))
    
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_urls = ['https://republic.com' + url for url in project_urls]
    
    for i in range(0, len(project_urls)):
        print(project_urls[i])
    
    print('republic after getting project urls')    
    
    project_datas = sc.scrape_projects(data_to_extract, project_urls)
    
    print('republic after scraping projects')
    
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
    with sc.scraper_context():
        #conda()
       # seedrs()
        #republic()
        econeers()