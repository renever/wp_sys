# - * - coding:utf-8 - * -
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0

url_login = 'http://www.uploadable.ch/login.php'
url_download = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'


ffprofile = webdriver.FirefoxProfile("/home/l/.mozilla/firefox/mwad0hks.default")

driver = webdriver.Firefox(ffprofile)

driver.get(url_login)



inputElement_userName = driver.find_element_by_name("userName")
inputElement_userPassword = driver.find_element_by_name("userPassword")
inputElement_userName.clear()
inputElement_userPassword.clear()

inputElement_userName.send_keys('lxl001')
inputElement_userPassword.send_keys('qQ2@wW')

btn_login = driver.find_element_by_id("loginFormSubmit")
btn_login.click()


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard_button")))
driver.get(url_download)
