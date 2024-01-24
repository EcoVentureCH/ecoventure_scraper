from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# setup chrome driver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# copy XPATH from website -> read html from website
clock_xpath = '//*[@id="ct"]'
driver.get('https://www.timeanddate.com/worldclock/switzerland')
clock = driver.find_element(By.XPATH, clock_xpath)
time_str = clock.get_attribute('innerHTML')

print(driver.title)
print(time_str)

driver.quit()
