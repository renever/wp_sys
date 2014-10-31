# - * - coding:utf-8 - * -
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0

url_login = 'http://www.uploadable.ch/login.php'
# url_download = 'http://pdl.uploadable.ch/file/SwkwFPd7scRC/yJjjJPhBdYlJIVTFXbCBgG0K77t5yexeS1SMccAZUPpTkUjjVCx4Yf86FyYTYDsKhdKryZC_e4_h9Ezc-ZfP0RQroH5C4v3gAyHOaMr85vSTHxjZQY9g-XdCY6FlWSTR12fS_S96MNRKjicseawPW69Xfge3QYdlULaAPv6yc9Y./123.pdf'
url_download = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'

ffprofile = webdriver.FirefoxProfile("/home/lotaku/.mozilla/firefox/mwad0hks.default")

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# go to the google home page
driver.get(url_login)

# the page is ajaxy so the title is originally this:
print driver.title

# find the element that's name attribute is q (the google search box)
inputElement_userName = driver.find_element_by_name("userName")
inputElement_userPassword = driver.find_element_by_name("userPassword")
inputElement_userName.clear()
inputElement_userPassword.clear()
# type in the search
inputElement_userName.send_keys('lxl001')
inputElement_userPassword.send_keys('qQ2@wW')

btn_login = driver.find_element_by_id("loginFormSubmit")
btn_login.click()


try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard_button")))
    driver.get(url_download)
    a = driver.switch_to_alert()
    a.accept()
except Exception,e:
    print 'start down...'


print "...."
print '2'
print '3'
print '4'
# except:
# 	print "没有找到登录按钮"
# 	driver.quit()
#
#
# try:
# 	# we have to wait for the page to refresh, the last thing that seems to be updated is the title
# 	WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element("span", "Download Now"))
# 	print 'find download btn'
# 	btn_download = driver.find_element_by_id("btn_premium_dl")
# 	btn_download.click()
# 	print 'get???'
# 	driver.page_source()
# 	WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(driver))
# 	driver.page_source()
#
# except Exception , e:
# 	print driver.title