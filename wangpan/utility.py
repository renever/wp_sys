# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
import logging
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
import time
from datetime import datetime

def create_session(engine, base):
	Session = sessionmaker(bind=engine)  # 创建一个Session类
	session = Session()  # 生成一个Session实例

	return session


def wp_logging(level='debug', Msg='Msg',allow_print=True):
	if level=='debug':
		if allow_print:
			print Msg
		logging.debug(Msg)
		return

def get_or_create(session, model, defaults=None, filter_cond=None,**kwargs):
	if filter_cond is not None:
		instance = session.query(model).filter_by(**filter_cond).first()
	else:
		instance = session.query(model).filter_by(**kwargs).first()
	if instance:
		# 文章存在 --> 返回文章实例 ，True
		return instance, True
	else:
		# params = dict((k, v) for k, v in kwargs.iteritems())
		# params.update(defaults or {})
		instance = model(**kwargs)
		session.add(instance)
		# 文章不存在 --> 返回文章实例 ，True
		return instance, False



class FirefoxDriver():

	def __init__(self):
		self.login_url = 'http://www.uploadable.ch/login.php'
	# url_login = 'http://www.uploadable.ch/login.php'
	# url_download = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'


		self.ffprofile = webdriver.FirefoxProfile("/home/l/.mozilla/firefox/mwad0hks.default")
		self.driver = None
		self.create_time = datetime.now()
	def get_new_driver(self):
		driver =  webdriver.Firefox(self.ffprofile)
		driver.get(self.login_url)
		inputElement_userName = driver.find_element_by_name("userName")
		inputElement_userPassword = driver.find_element_by_name("userPassword")
		inputElement_userName.clear()
		inputElement_userPassword.clear()

		inputElement_userName.send_keys('lxl001')
		inputElement_userPassword.send_keys('qQ2@wW')

		btn_login = driver.find_element_by_id("loginFormSubmit")
		btn_login.click()


		WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard_button")))
		return driver

	def download_file(self,url_inst):
		try:
			self.driver.get(url_inst.url)
			time.sleep(3)
			Msg = "开始下载文件：%s" % url_inst.url
			wp_logging(Msg=Msg)
		except Exception,e:
			Msg = 'Error(下载文件)--> 异常信息（%s);文章ID（%s）;下载链接（%s） ' % (e, url_inst.article_id, url_inst.url)
			wp_logging(Msg=Msg)
			raise e


	def driver_quit(self):
		self.driver.quit()

	#todo 如果下载出现HTML文件，cooki过期，或者定义为每20分钟重新登录一次。