'''
test scraper for scraping active projects on www.conda.ch
'''
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


CSV_FNAME = 'conda.csv'
ATTRIBUTE_TIMEOUT = 3

# attr_name : (css selector, html attribute | re.comile('..'))
# regex tries to findall in innerHTML
ATTRIBUTE_CSS_SELECTORS = {
    'external_link' : ('meta[property="og:url"]', 'content'),
    'name': ('meta[property="og:title"]', 'content') ,
    'image': ('meta[property="og:image"]', 'content'),
    'min_investment': ('p.min-investment', re.compile(r'(?:\d*\.)?\d+')),
}


def update_csv(attributes_list):
    
    print(f'INFO: writing entries to {CSV_FNAME}')
    with open(CSV_FNAME, 'w') as f:
        f.write('# ')
        for attr_name in attributes_list[0].keys():
            f.write(attr_name + ', ')
        f.write('\n')

        for attributes in attributes_list:
            for value in attributes.values():
                if value is None:
                    value = ''
                f.write(value + ', ')
            f.write('\n')

def read_projects_conda(driver, url='https://www.conda.ch/projekte-entdecken/'):
    driver.get(url)

    # accept cookies
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'CookieBoxSaveButton'))
        ).click()
    except exceptions.ElementNotInteractableException as e:
        print("INFO: cookies accept thing not Interactable")

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


    campaign_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'campaign-load-me'))
    )


    attributes_list = []
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
                            print(regex_result)
                except exceptions.TimeoutException as e:
                    print(f'WARNING: didn\'t find attribute {attribute_name} on page {campaing_url} waiting for {ATTRIBUTE_TIMEOUT} seconds')
                    continue

                attributes[attribute_name] = value
            
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            attributes_list.append(attributes)
            print(attributes)
    update_csv(attributes_list)


# setup chrome driver
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
read_projects_conda(driver)
driver.quit()
