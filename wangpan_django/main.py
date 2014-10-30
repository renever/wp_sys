# -*- coding: utf-8 -*-
from pyvirtualdisplay import Display
from selenium import webdriver
from utils import login_to_uploadable
import time
# display = Display(visible=0, size=(800, 600))
# display.start()
url = 'http://www.uploadable.ch/login.php'
url_download = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'
r = login_to_uploadable()
d = dict(r.cookies)
print dir(d)
print d
# d2 = {u'domain': u'www.uploadable.ch', u'name': u'', u'value': u'', u'expiry': None, u'path': u'', u'secure': False}
# browser = webdriver.Chrome()
browser = webdriver.Firefox()
# time.sleep(3)
browser.get(url)

username = browser.find_element_by_id("userName")
password = browser.find_element_by_id("userPassword")

username.send_keys("lxl001")
password.send_keys("qQ2@wW")

browser.find_element_by_id("loginFormSubmit").click()
browser.
# browser.get(url_download)
# browser.add_cookie(d)
# a = browser.get_cookies()
# print a
# browser.get('http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf')


# browser.add_cookie(dict(r.cookies))
# browser.get('http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf')
# # browser.get('http://www.baidu.com')
# a = browser.get_cookies()
# print a
# browser.delete_all_cookies()
# # for cookie in d:
# #     print "add cookie:",cookie
# #     browser.add_cookie(cookie)
# browser.add_cookie(d)
#
# a = browser.get_cookies()
# print a

# btn_download = browser.find_element_by_id('btn_premium_dl')
# link_download = btn_download.click()
# print link_download

# display.stop()

# ---------ghost-----------
# from ghost import Ghost
# ghost = Ghost()
# page, extra_resources = ghost.open("http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf")
# # assert page.http_status==200 and u'百度' in ghost.content
# print page.http_status
# print ghost.content
#----------end ghost ---------