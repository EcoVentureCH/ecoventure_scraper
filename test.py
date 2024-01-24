from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

clock_xpath = '//*[@id="ct"]'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('log-level=3')
driver = webdriver.Chrome(options=chrome_options)


driver.get('https://www.timeanddate.com/worldclock/switzerland')
clock = driver.find_element(By.XPATH, clock_xpath)
time_str = clock.get_attribute('innerHTML')

print(driver.title)
print(time_str)

driver.quit()
