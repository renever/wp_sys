# - * - coding:utf-8 - * -
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
import time
url_login = 'http://www.uploadable.ch/login.php'
# url_download = 'http://pdl.uploadable.ch/file/SwkwFPd7scRC/yJjjJPhBdYlJIVTFXbCBgG0K77t5yexeS1SMccAZUPpTkUjjVCx4Yf86FyYTYDsKhdKryZC_e4_h9Ezc-ZfP0RQroH5C4v3gAyHOaMr85vSTHxjZQY9g-XdCY6FlWSTR12fS_S96MNRKjicseawPW69Xfge3QYdlULaAPv6yc9Y./123.pdf'
url_download = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'

# ffprofile = webdriver.FirefoxProfile("/home/lotaku/.mozilla/firefox/mwad0hks.default")
ffprofile = webdriver.FirefoxProfile("/home/l/.mozilla/firefox/mwad0hks.default")
# ffprofile = webdriver.FirefoxProfile()
# ffprofile.set_preference("browser.download.folderList",2)
# # Create a new instance of the Firefox driver
#
# ffprofile.set_preference("browser.download.dir", '/home/l/test_down')
# ffprofile.set_preference("browser.helperApps.neverAsk.saveToDisk",'application/pdf')
#
# # disable Firefox's built-in PDF viewer
# ffprofile.set_preference("pdfjs.disabled",True)
#
# # disable Adobe Acrobat PDF preview plugin
# ffprofile.set_preference("plugin.scan.plid.all",False)
# ffprofile.set_preference("plugin.scan.Acrobat", "99.0")

driver = webdriver.Firefox(ffprofile)
# driver = webdriver.Chrome()

# go to the google home page

driver.get("http://www.baidu.com")
# the page is ajaxy so the title is originally this:
print driver.title

# find the element that's name attribute is q (the google search box)
inputElement_kw = driver.find_element_by_id("kw")
# inputElement_userPassword = driver.find_element_by_name("userPassword")
inputElement_kw.clear()
# inputElement_userPassword.clear()
# type in the search
inputElement_kw.send_keys('qq')
# inputElement_userPassword.send_keys('qQ2@wW')

btn_search = driver.find_element_by_id("su")


btn_search.click()
driver.get("http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=98765000_hao_pg&wd=qq&rsv_enter=0&rsv_sug3=1&rsv_sug4=59&rsv_sug1=1&inputT=10283")

try:
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "c-gap-left-small")))
	print "开始找按钮--普通下载"
	btn_down = driver.find_element_by_link_text(u'普通下载')
	btn_down.click()
	# a = driver.switch_to.alert
	# a.accept()
	time.sleep(5)


except Exception, e:
	print "错了！"
	print e

print "...."
print '2'
print '3'
print '4'
time.sleep(20)
# except:
# print "没有找到登录按钮"
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