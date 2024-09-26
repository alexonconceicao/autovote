from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from time import sleep

chrome_service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=chrome_service)
driver.get("https://www.google.com")
sleep(5)
driver.quit()
