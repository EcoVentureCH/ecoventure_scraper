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

from src.field_parsers import parse_amount_and_currency, parse_currency, parse_amount
import src.scraper_api as sc
from src.utils import print_flushed as print

def conda():

    # TODO: add projects that have 'starting in ... days'

    url = 'https://www.conda.ch/projekte-entdecken/'

    data_to_extract = {
        'name':                 r'<meta\W+property=\"og:title\"\W+content=\"(.*?)\">',
        'name_short':           r'<meta\W+property=\"og:title\"\W+content=\"(.*?)\">',
        'external_link':        r'<meta\W+property=\"og:url\"\W+content=\"(.*?)\">',
        'external_image_link':  r"<meta\W+property=\"og:image\"\W+content=\"(.*?)\">",
        'funding_current':      r"<p class=\"conda-knob-value-text\".*?>(.*?CHF)</p>",
        'funding_min':          r"Mindestinvestition:(\W+CHF\W+\d*?\.[\-\d])",
        'funding_target':       lambda bfs: sc.text_from_class(bfs, 'p', 'total-amount'),
        'description':          r"<p class=\"text-white large italic text-shadow-dark\">(.*?)</p>",
        'description_short':    r"<p class=\"text-white large italic text-shadow-dark\">(.*?)</p>",
    }

    sc.open(url)
    sc.accept_cookies((By.ID, 'CookieBoxSaveButton'))
    sc.click_through((By.ID, "campaigns_load_more_btn"))

    html_project_page = sc.get_html()
    regex_projects_urls = r'<a href="(https://www\.conda\.ch/.*?)".*?class="i-btn i-btn-secondary text-uppercase">'

    # TODO(#15): check if all urls are valid!
    # handle error in sc.scrape_projects later
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_datas = sc.scrape_projects(data_to_extract, project_urls)

    # set location and currency for all projects
    # TODO: make this code smaller
    for i in range(len(project_datas)):
        project_datas[i]['location'] = "Switzerland"

        currency = parse_currency(project_datas[i]['funding_min'])
        project_datas[i]['currency'] = currency
        project_datas[i]['funding_min'] = parse_amount(project_datas[i]['funding_min'])
        project_datas[i]['funding_current'] = parse_amount(project_datas[i]['funding_current'])
        project_datas[i]['funding_target'] = parse_amount(project_datas[i]['funding_target'])

    return project_datas


def seedrs_raising():

    url = 'https://www.seedrs.com/invest/raising-now'

    data_to_extract = {
        'name':                lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'name_short':          lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':       lambda bfs: sc.text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'external_image_link': lambda bfs: sc.text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'funding_min':         lambda bfs: sc.text_from_class(bfs, 'span', 'highlights-extra-info'),
        'funding_target':      lambda bfs: sc.text_from_class(bfs, 'div', 'investment_total_target'),
        'funding_current':     lambda bfs: sc.text_from_class(bfs, 'div', 'CampaignProgress-text'),
        'description_short':   lambda bfs: sc.text_from_class(bfs, 'p', 'summary'),
        'description':         lambda bfs: sc.text_from_class(bfs, 'p', 'summary'),
        'location':            lambda bfs: sc.text_from_class(bfs, 'tr', 'location').replace("\n", " "),
    }

    sc.open(url)

    for i in range(10):
        sc.scroll_down(400)
        time.sleep(1)

    regex_projects_urls = r'<a href=\"(/[a-zA-Z\-\d\_]+?)\">'
    html_project_page = sc.get_html()
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    project_urls = ['https://www.seedrs.com' + url for url in project_urls]

    project_datas = sc.scrape_projects(data_to_extract, project_urls)

    for i in range(len(project_datas)):
        currency = parse_currency(project_datas[i]['funding_min'])
        project_datas[i]['currency'] = currency
        project_datas[i]['funding_min'] = parse_amount(project_datas[i]['funding_min'])
        project_datas[i]['funding_current'] = parse_amount(project_datas[i]['funding_current'].split("from")[0])
        project_datas[i]['funding_target'] = parse_amount(project_datas[i]['funding_target'])

    return project_datas
    

# disabled for now (_ disables it!)
def _republic():
    data_to_extract = {
        'name':           lambda bfs: sc.text_from_class(bfs, 'h1', 'h2 favourite'),
        'external_link':  lambda bfs: sc.text_from_class(bfs, 'meta', 'og:url', 'property', key='content'),
        'image':          lambda bfs: sc.text_from_class(bfs, 'meta', 'og:image', 'property', key='content'),
        'min_investment': lambda bfs: sc.text_from_class(bfs, 'div', 's-marginTop0_5 u-textCenter s-fontSize14 u-fontWeight400 u-colorMuted'),
        'funding_target': lambda bfs: sc.text_from_class(bfs, 'div', 'u-fontWeight600 u-textRight s-marginLeft1 offerings-show-flexible_deal_terms-item__value'),
        'progress':       lambda bfs: sc.text_from_class(bfs, 'div', 's-marginBottom1_5 s-borderBottom1_5 offerings-show-header-raised_amount')
    }
    
    print('republic test start')
    
    url = 'https://republic.com/companies'
    
    sc.open(url)
    
    sc.scroll_down(40000)
    time.sleep(1)
    sc.scroll_down(40000)
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

    for i in range(len(project_datas)):
        currency = parse_currency(project_datas[i]['funding_min'])
        project_datas[i]['currency'] = currency
        project_datas[i]['funding_min'] = parse_amount(project_datas[i]['funding_min'])
        project_datas[i]['funding_current'] = parse_amount(project_datas[i]['funding_current'])
        project_datas[i]['funding_target'] = parse_amount(project_datas[i]['funding_target'])

    
    return project_datas
    
# disabled for now (_ disables it!)
def _econeers():

    url = 'https://www.econeers.de/#aktuelle-investmentchancen'

    data_to_extract = {
        #'name': lambda bfs: sc.text_from_class(bfs, 'meta',   'og:description', 'property', key='content'),
        'name':                lambda _: "Test Name",
        'name_short':          lambda _: "Test Name Short",
        'description':         lambda _: "Long Long Description",
        'description_short':   lambda _: "Descr short",
        'location':            lambda _: "it",
        'external_link':       lambda bfs: sc.text_from_class(bfs, 'meta',  'og:url', 'property', key='content'),
        'external_image_link': lambda bfs: sc.text_from_class(bfs, 'meta',   'og:image', 'property', key='content'),
        'funding_min':         lambda bfs: sc.text_from_class(bfs, 'td', 'tg-kftd'),
        'funding_target':      lambda bfs: sc.text_from_class(bfs, 'td', 'tg-lqy6'),
        'funding_current':     lambda bfs: sc.text_from_class(bfs, 'h2', 'center-text')
    }
        
    sc.open(url)
    
    html_project_page = sc.get_html()
    #print(html_project_page)
    
    regex_projects_urls = r'<a\W+href=\"(https:\/\/www\.econeers\.de\/[^\"].+?)\"'
    project_urls = re.findall(regex_projects_urls, html_project_page, re.MULTILINE)
    
    print("project urls: ")
    print(project_urls)

    project_datas = sc.scrape_projects(data_to_extract, project_urls)
        
    for i in range(len(project_datas)):
        currency = parse_currency(project_datas[i]['funding_min'])
        project_datas[i]['currency'] = currency
        project_datas[i]['funding_min'] = parse_amount(project_datas[i]['funding_min'])
        project_datas[i]['funding_current'] = parse_amount(project_datas[i]['funding_current'])
        project_datas[i]['funding_target'] = parse_amount(project_datas[i]['funding_target'])

    return project_datas


if __name__ == "__main__":
    with sc.scraper_context(debug=False):
        #print(conda())
        #print(seedrs_raising())
        #print(_republic())
        print(_econeers())


# TODO: from Yannic, add useful parts of this to api later if needed..
'''
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
'''