# - * - coding:utf-8 - * -
from settings import FFPROFILE
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
import time

url_login = 'http://www.uploadable.ch/login.php'
filesystem = 'http://www.uploadable.ch/filesystem.php'


ffprofile = webdriver.FirefoxProfile("/home/lotaku/.mozilla/firefox/mwad0hks.default")

driver = webdriver.Firefox(FFPROFILE)

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
driver.get(filesystem)
time.sleep(2)

#todo 增加判断 Ftp文件夹里面的文件数量，if is 0, break。

btn_show_files = driver.find_element_by_xpath("/html/body/div[8]/div[5]/div[1]/form/ul/li[7]/a/span/span[1]/font[1]")
btn_show_files.click()
time.sleep(2)

# set show 1000
# try:
#     selector_show_1000_files_per_page = driver.find_element_by_xpath('//*[@id="filesPerPageDropDownList"]/option[@value="1000"]')
#     selector_show_1000_files_per_page.click()
#     time.sleep(3)
# except Exception , e:
#     print e
#     print 'less than 50,pass...'
#     pass

btn_select_all_files = driver.find_element_by_xpath("/html/body/div[8]/div[4]/div/ul/li[4]/a[1]")
btn_select_all_files.click()
time.sleep(2)
btn_with_file_name = driver.find_element_by_xpath('//*[@id="with_file_name"]')
btn_with_file_name.click()
time.sleep(2)
text_links = driver.find_element_by_xpath('//*[@id="link_textarea"]')
print text_links.text
#move
btn_move = driver.find_element_by_xpath('//*[@id="toolMoveFile"]')
btn_move.click()
time.sleep(2)

btn_move_chose_done_dir = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[2]/div[2]/form/div/div/div/ul/ul/li[1]/a/span/input')
btn_move_chose_done_dir.click()
time.sleep(2)

btn_move_start = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div[1]/div/a')
btn_move_start.click()
time.sleep(2)

btn_move_done = btn_move_start = driver.find_element_by_xpath('//*[@id="closeErrMsg"]')
btn_move_done.click()
time.sleep(2)