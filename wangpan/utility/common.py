# -*- coding: utf-8 -*-
from __future__ import division
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from datetime import datetime

import humanize
import os
import shutil
from ftplib import FTP
import requests
from contextlib import closing
from pyquery import PyQuery as pq



# #scoped_session 线程安全
# def create_scoped_session(engine, base):
# 	Session = sessionmaker(bind=engine)  # 创建一个Session类
# 	session = scoped_session(Session)  # 生成一个Session实例
#
# 	return session

# def wp_logging(level='debug', Msg='Msg',allow_print=True):
# 	if level=='debug':
# 		if allow_print:
# 			print Msg
# 		logging.debug(Msg)
# 		return

# def get_or_create(session, model, is_global=False, defaults=None, filter_cond=None,**kwargs):
# 	"""
# 	@is_global=False #db_session 是不是全局性的，是，则不能在这里关闭。
# 	"""
# 	created = None
# 	if filter_cond is not None:
# 		instance = session.query(model).filter_by(**filter_cond).first()
# 	else:
# 		instance = session.query(model).filter_by(**kwargs).first()
# 	if instance:
# 		created = False
# 		# 文章存在 --> 返回文章实例 ，(没有新建）False
# 		if not is_global:
# 			session.close()
# 		return instance,created
# 	else:
# 		created = True
# 		# params = dict((k, v) for k, v in kwargs.iteritems())
# 		# params.update(defaults or {})
# 		instance = model(**kwargs)
# 		if not is_global:
# 			session.add(instance)
# 			session.commit()
# 			session.close()
# 		# 文章不存在 --> 返回文章实例 ，(有新建）True
# 		return instance, created

# class FirefoxDriver():
#
# 	def __init__(self):
# 		self.login_url = 'http://www.uploadable.ch/login.php'
# 	# url_login = 'http://www.uploadable.ch/login.php'
# 	# url_download = 'http://www.uploadable.ch/file/SwkwFPd7scRC/123.pdf'
#
#
# 		self.ffprofile = webdriver.FirefoxProfile(FirefoxProfilePath)
# 		self.driver = None
# 		self.create_time = datetime.now()
# 		self.login_time = None
# 	def get_new_driver(self):
# 		driver =  webdriver.Firefox(self.ffprofile)
# 		driver.get(self.login_url)
# 		inputElement_userName = driver.find_element_by_name("userName")
# 		inputElement_userPassword = driver.find_element_by_name("userPassword")
# 		inputElement_userName.clear()
# 		inputElement_userPassword.clear()
#
# 		inputElement_userName.send_keys('lxl001')
# 		inputElement_userPassword.send_keys('qQ2@wW')
#
# 		btn_login = driver.find_element_by_id("loginFormSubmit")
# 		btn_login.click()
#
#
# 		WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard_button")))
# 		return driver
#
# 	def download_file(self,url_inst):
# 		status = False      #True表示程序已经成功开始下载文件
# 		db_session = create_session()
# 		db_session.add(url_inst)
# 		try:
# 			self.driver.get(url_inst.url)
# 			# time.sleep(3)
# 			# Msg = "开始下载文件：%s" % url_inst.url
# 			# wp_logging(Msg=Msg)
# 			status = True
# 		except Exception,e:
# 			Msg = '下载文件出错！ 异常信息（%s);文章ID（%s）;下载链接（%s） ' % (e, url_inst.article_id, url_inst.url)
# 			wp_logging(Msg=Msg)
# 			raise e
# 		db_session.close()
# 		return status
#
# 	def driver_quit(self):
# 		self.driver.quit()
#
# 	#todo 如果下载出现HTML文件，cooki过期，或者定义为每20分钟重新登录一次。



# common_utility.get_rared_files_name('/home/l/app/learning/wangpan/wp_resource/articles_file/1/rared_files/')

import subprocess, threading

class ShellCommand(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None

	def run(self, timeout):
		def target():
			print 'Shell Thread started'
			self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = self.process.communicate()
			print 'Shell Thread finished'
		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			print 'Terminating Shell process'
			self.process.terminate()
			return {'status': 'Time Out'}
		s =  self.process.returncode
		# print s
		#成功时，s==0
		return {'status': s}

	def check_stdout(self,str,out):
		#可以判断返回信息包含哪些信息
		import re
		result = re.findall(str,out,re.MULTILINE)
		if result:
			return u'成功的out里找到str'
		else:
			return u'在out里面找不到str'


class FilmAvFtp():

	def __init__(self,host='ftp.uploadable.ch',user='lxl001',password='f19174de',port=21,blocksize=8192):
		self.host = host
		self.user = user
		self.password = password
		self.port = port
		self.ftp=FTP(host)
		self.blocksize = blocksize

	def login(self):
		self.ftp.login(user=self.user, passwd=self.password)

	# def handle(self):
	#
	# 	pass
	#
	# def upload_list(self,full_path_file_names):
	#
	# 	for full_path_file_name in full_path_file_names:
	# 		file_name = os.path.basename(full_path_file_name)
	# 		with open(full_path_file_name,'rb') as f:
	# 			try:
	# 				myFtp.ftp.storbinary('STOR ' + file_name,
	# 						   f,
	# 						   self.blocksize,
	# 						   self.callback_handle(file_name))
	# 			except ftplib.error_perm :
	# 				print "上传失败！"
	# 			print "%s 上传成功。" % file_name
	#
	# def upload(self,full_path_file_name):
	# 	new_ftp = MyFtp()
	# 	new_ftp.login()
	#
	# 	file_name = os.path.basename(full_path_file_name)
	# 	with open(full_path_file_name,'rb') as f:
	# 		try:
	# 			new_ftp.ftp.storbinary('STOR ' + file_name,
	# 					   f,
	# 					   self.blocksize,
	# 					   self.callback_handle(file_name))
	#
	# 		except ftplib.error_perm :
	# 			print "上传失败！"
	# 		print "%s 上传成功。" % file_name
	#
	# def callback_handle(self,file_name):
	# 	print "%s 上传中..." % file_name



# 测试
# file_path = '/home/l/app/learning/wangpan/wp_resource/articles_file/1/downloaded_files/chrome.part4.rar'
#
# dir = '/home/l/app/learning/wangpan/wp_resource/articles_file/1/unrared_files'
#
# cmd = '/usr/bin/unrar x ' + file_path +' ' + dir
#
# command = ShellCommand(cmd)
# # command.run(timeout=10)
# # command.run(timeout=1)
#
#
# thread = threading.Thread(target=command.run,kwargs={'timeout':3})
# thread.setDaemon(True)
# thread.start()
# print 'a'
# time.sleep(1)
# print '1'
# thread.join(2)
# print '2'


