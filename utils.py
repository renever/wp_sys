# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
import logging
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
# from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
import time
from datetime import datetime
from settings import FirefoxProfilePath,DB_ENGINE, DB_BASE,CHUNK_SIZE
#DIR
from settings import ARTICLE_FILES_DIR
import humanize
import os
import requests
from contextlib import closing
from pyquery import PyQuery as pq
import shutil
import json
from models import NewDownloadLink
import re
def create_session(engine=DB_ENGINE, base=DB_BASE):
	Session = sessionmaker(bind=engine)  # 创建一个Session类
	session = Session()  # 生成一个Session实例

	return session
#scoped_session 线程安全
def create_scoped_session(engine, base):
	Session = sessionmaker(bind=engine)  # 创建一个Session类
	session = scoped_session(Session)  # 生成一个Session实例

	return session

def wp_logging(level='debug', Msg=u'Msg',allow_print=True):
	if level=='debug':
		if allow_print:
			print Msg
		logging.debug(Msg)
		return

def get_or_create(session, model, is_global=False, defaults=None, filter_cond=None,**kwargs):
	"""
	@is_global=False #db_session 是不是全局性的，是，则不能在这里关闭。
	"""
	created = None
	if filter_cond is not None:
		instance = session.query(model).filter_by(**filter_cond).first()
	else:
		instance = session.query(model).filter_by(**kwargs).first()
	if instance:
		created = False
		# 文章存在 --> 返回文章实例 ，(没有新建）False
		if not is_global:
			session.close()
		return instance,created
	else:
		created = True
		# params = dict((k, v) for k, v in kwargs.iteritems())
		# params.update(defaults or {})
		instance = model(**kwargs)
		if not is_global:
			session.add(instance)
			session.commit()
			session.close()
		# 文章不存在 --> 返回文章实例 ，(有新建）True
		return instance, created

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
# 			Msg = 'Error(下载文件)--> 异常信息（%s);文章ID（%s）;下载链接（%s） ' % (e, url_inst.article_id, url_inst.url)
# 			wp_logging(Msg=Msg)
# 			raise e
# 		db_session.close()
# 		return status
#
# 	def driver_quit(self):
# 		self.driver.quit()
#
# 	#todo 如果下载出现HTML文件，cooki过期，或者定义为每20分钟重新登录一次。

class CommonUtility():

	def get_file_size(self, file_path, gnu=True, format='%.2f'):
		# return humanize.naturalsize(os.path.getsize(file_path),gnu=True,format=format)
		return os.path.getsize(file_path)

	def move_file_to_dir(self,file_path,dir):
		if not os.path.exists(dir):
			os.makedirs(dir)
		# os.rename(file_path,dir)
		shutil.move(file_path,dir)

	def get_files_in_dir(self, dir_path):
		file_names = os.listdir(dir_path)
		filtered_file_name = []
		for name in file_names:
			#临时测试压缩
			if name=='chromedriver':
				filtered_file_name.append(name.encode('utf8'))
			try:
				# print name.encode('utf8')
				ext = name.split('.')[1].lower()
				# print ext.encode('utf8')
				if ext.encode('utf8') in ['avi','mp4']:

					filtered_file_name.append(name.encode('utf8'))
			except:
				pass
		return filtered_file_name

	def get_files_with_pull_path(self, dir_path):
		files_with_abspath = []
		for dirname, dirnames, filenames in os.walk(dir_path):
			for filename in filenames:
				files_with_abspath.append(os.path.join(dirname, filename))
		return files_with_abspath

	def get_rared_files_name(self, dir_path):
		#返回已经压缩好的文件名（位于rared 文件夹）
		files_name = []
		for dirname, dirnames, filenames in os.walk(dir_path):
			for filename in filenames:
				files_name.append(filename)

		return files_name


common_utility = CommonUtility()

class GrabNewODL():
	'''
	抓取新的下载地址
	'''
	def __init__(self):
		self.data = {
			'userName': 'lxl001',
			'userPassword': 'qQ2@wW',
		    'autoLogin':'on',
		    'action__login':'normalLogin'
		}

		self.headers = {
			'Request URL': 'http://www.uploadable.ch/login.php',
			'Accept-Encoding': 'gzip,deflate,sdch',
			'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.',
			'Connection': 'keep-alive',
			'Host': 'www.uploadable.ch',
			'Referer': 'http://www.uploadable.ch/login.php',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
		}
		self.url = 'http://www.uploadable.ch/login.php'
		self.url_filesystem = 'http://www.uploadable.ch/filesystem.php'
		self.r_session = requests.session()
		self.try_download_count = 0
		self.total_size = 0
		self.logining = False
		self.dir_delete_id = 263083
		self.dir_done_id = 210640
#http://www.uploadable.ch/file/dQADKukpsKjn/chrome.part1.rar
	def login(self):
		self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.logining = True


	# def grab_ndls(self):
	# 	'''
	# 	post url:http://www.uploadable.ch/file-manager-expand-folder.php
	# 	post data --1:
	# 			current_page	1
	# 			parent_folder_id	197173
	# 			sort_field	0
	# 			sort_order	ASC
	# 			total_folder_count	0
	# 	post data --2: 显示1000文件
	# 			current_page	1
	# 			extra	filesPanel
	# 			files_per_page	1000
	# 			is_search	false
	# 			parent_folder_id	197164
	# 			sort_field	0
	# 			sort_order	ASC
	# 			total_folder_count	0
	#
	# 	'''''
	#
	#
	# 	# with closing(requests.get(url=self.url_filesystem, stream=True, cookies=self.r.cookies,allow_redirects=True)) as a:
	# 	# 	print a.content
	# 	page = self.r_session.get(url=self.url_filesystem,allow_redirects=True)
	# 	# page = requests.get(url=self.url_filesystem,stream=True,cookies=self.r.cookies,allow_redirects=True)
	# 	# (url, stream=True, cookies=r.cookies,allow_redirects=True)
	# 	print "*"*99
	# 	print page.content
	# 	page_text = pq(page.text)
	# 	download_links = page_text("label[name='download_link']")
	# 	print download_links

	def download(self,url_inst=None):

		'''
		用requests下载测试
		'''

		db_session = create_session()
		db_session.add(url_inst)
		print url_inst.url

		file_dir = ARTICLE_FILES_DIR +'/'+ str(url_inst.article_id) +'/downloaded_files/'
		file_path = file_dir+url_inst.file_name
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)


		file_size_dl = 0

		# todo 下载是有效的下载方法，可以增大chunk_size
		with open(file_path, 'wb') as local_file:
			try:
				file = self.r_session.get(url_inst.url, stream=True, allow_redirects=True)
				# file = self.r_session.post(url_inst.url, data = {'stream':True, 'allow_redirects':True})
			except requests.exceptions.Timeout as e:
				db_session.close()
				return 'Download Time out'
				# with closing(self.r_session.get(url_inst.url, stream=True, allow_redirects=True)) as file:
			#file.history
			# print file.headers
			self.total_size = int(file.headers['content-length'])

			# 更新下载文件的实际大小
			url_inst.file_size = self.total_size
			db_session.add(url_inst)
			db_session.commit()
			Msg = u'更新下载文件(%s)的实际大小' % url_inst.file_name
			wp_logging(Msg=Msg,allow_print=True)

			if 'http://pdl' not in file.url:
				#尝试下载5次不成功，则放弃
				if self.try_download_count > 5:
					db_session.close()
					Msg = u'Try more times than 5 (link: %s )' % url_inst.url
					wp_logging(Msg=Msg)
					return u'尝试下载5次不成功'
				self.try_download_count += 1
				self.login()
				db_session.close()
				return self.download(url_inst)

			for content in file.iter_content(CHUNK_SIZE):
				if content:  # filter out keep-alive new chunks
					file_size_dl += len(content)
					local_file.write(content)
					local_file.flush()
					completeness = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / self.total_size)
					completeness = completeness + chr(8)*(len(completeness)+1)
					Msg = u'{file_name} 下载进度：{completeness}'\
						.format(file_name=url_inst.file_name, completeness=completeness)
					wp_logging(Msg=Msg, allow_print=True)
		if file_size_dl == self.total_size:
			db_session.close()
			return 'Download successful'
		else:
			db_session.close()
			return 'Download fail'




	def get_new_uploaded_file_url(self):
		'''
		'''
		url = 'http://www.uploadable.ch/file-manager-expand-folder.php'
		data = {
			'current_page':	     '1',
			'extra':	        'filesPanel',
			'files_per_page':	'1000',
			'is_search':	    'false',
			'parent_folder_id':	'197173',
			'sort_field':	    '0',
			'sort_order':	    'ASC',
			'total_folder_count':'0',
		}

		r = self.r_session.post(url=url,data=data, allow_redirects=True)
		# print r.text
		return r.text
		# print r.text

	def para_new_url(self,json_data={}):
		db_session = create_session()
		# false = 'false'
		# a = {}
		# for i in a['uploads']:
		# 	for k,v in i.iteritems():
		# 		print k,':',v
		# 	print "-"*99
		json_data = json.loads(json_data)
		file_ids = []
		file_ids_deleted = []
		for file in json_data['uploads']:
			file_name = file.get('uploadFileName')
			file_size = int(file.get('fileSize'))
			file_size_in_view = file.get('fileSizeInView')
			file_id = file.get('uploadId')
			url = file.get('downloadLink')


			ndl_inst = db_session.query(NewDownloadLink).filter_by(file_name=file_name,url_type='uploadable.ch').first()
			if ndl_inst is not None:
				if int(ndl_inst.file_size) == file_size:
					ndl_inst.url = url
					ndl_inst.file_size_in_view = file_size_in_view
					db_session.add(ndl_inst)
					db_session.commit()
					file_ids.append(file_id)
					Msg = '更新%s 的新URL' % file_name.encode('utf8')
					wp_logging(Msg=Msg)
				else:#大小不相等，属于上传失败的文件，删除！
					file_ids_deleted.append(file_id)



		db_session.close()
		#none 和不相等的移动到delete_dir_id
		self.move_files_to_dir(files_list=file_ids_deleted, moveFolderDest=self.dir_delete_id)
		#已经更新的移动到done dir
		self.move_files_to_dir(files_list=file_ids, moveFolderDest=self.dir_done_id)


	def move_files_to_dir(self,files_list=[], CurrentFolderId=197173,moveFolderDest=210640 ):
		if not files_list:
			return
		data = dict(
			CurrentFolderId=CurrentFolderId,#ftp 文件ID 197173
			moveFolderDest=moveFolderDest,#done 文件夹ID 210640
			moveFolderId=', '.join(str(file_id) for file_id in files_list)
		)
		url = 'http://www.uploadable.ch/file-manager-action.php'
		try:
			r = self.r_session.post(url=url,data=data, allow_redirects=True)
		except Exception as e:
			raise e

	def update_urls(self):
		self.login()
		json_data = self.get_new_uploaded_file_url()
		self.para_new_url(json_data=json_data)


class GrabNewODL_UPNET():
	'''
	抓取新的下载地址
	'''
	def __init__(self):
		self.data = {
			'id': 'lxl001',
			'pw': '123qwe',
		}

		self.headers = {
			'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
			'Cache-Control': 'no-cache',
			'Connection': 'keep-alive',
			'Content-Length': '19',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Host':	'uploaded.net',
			'Pragma': 'no-cache',
			'Referer': 'http://uploaded.net/',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0',
			'X-Prototype-Version': '1.6.1',
			'X-Requested-With': 'XMLHttpRequest',

		}
		self.url = 'http://uploaded.net/io/login'
		self.url_filesystem = 'http://uploaded.net/manage'
		self.r_session = requests.session()
		self.try_download_count = 0
		self.total_size = 0
		self.logining = False
		self.dir_delete = 'hwsukj'
		self.dir_done = 'fmaszx'
		#done 文件夹 ：fmaszx
		#delete 文件夹：hwsukj
	def login(self):
		self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.logining = True



	def get_new_uploaded_file_url(self):
		'''
		'''
		url = 'http://uploaded.net/api/file/list'
		data = {
			'folder': '0',
			'max':'100',
			'nav':'undefined',
			'q':'',
			'start':'0',
		}

		#返回的数据格式
		responded_no_use = '''

		{"parent":{"id":"0","title":"root","parent":"0"},
"path_info":[{"id":"0","title":"root","parent":"0"}],
"folder":[
        {"title":"FTP","id":"nu98tc","parent":"0"},
        {"title":"done","id":"fmaszx","parent":"0"}],
"files_count":1,
"files":[
    {"filename":"wps_symbol_fonts.zip",
    "size":255720,
    "size_nice":"249,73 KB",
    "ext":"zip",
    "id":"9lr16lec",
    "admin":"werito",
    "_public":"0",
    "pass":false,
    "_private":false,
    "created":"2014-12-13 14:25:57",
    "created_nice":"13\/12\/2014",
    "folder":"0",
    "downloads":0,
    "downloads_last":"n\/A",
    "is_quarantined":false,
    "will_deleted_at":false}],
"pagination":[]}

		'''

		r = self.r_session.post(url=url,data=data, allow_redirects=True)
		return r.text

	def para_new_url(self,json_data={}):
		db_session = create_session()
		json_data = json.loads(json_data)
		file_ids = []
		file_ids_deleted = []
		if not json_data.get('files',None):
			return
		for file in json_data['files']:
			file_name = file.get('filename')
			file_size = int(file.get('size'))
			file_size_in_view = file.get('size_nice')
			file_id = file.get('id')
			# url 格式：http://uploaded.net/file/9lr16lec/wps_symbol_fonts.zip
			url = 'http://uploaded.net/file/' + file_id +'/' + file_name


			ndl_inst = db_session.query(NewDownloadLink).filter_by(file_name=file_name,url_type='uploaded.net').first()
			if ndl_inst is not None:
				if int(ndl_inst.file_size) == int(file_size):
					ndl_inst.url = url
					ndl_inst.file_size_in_view = file_size_in_view
					db_session.add(ndl_inst)
					db_session.commit()
					file_ids.append(file_id)
					Msg = '更新%s 的新URL' % file_name.encode('utf8')
					wp_logging(Msg=Msg)
				else:#大小不相等，属于上传失败的文件，删除！
					file_ids_deleted.append(file_id)



		db_session.close()
		#none 和不相等的移动到delete_dir_id
		self.move_files_to_dir(files_list=file_ids_deleted, to=self.dir_delete)
		#已经更新的移动到done dir
		self.move_files_to_dir(files_list=file_ids, to=self.dir_done)


	def move_files_to_dir(self,files_list=[], to='fmaszx',):
		#done 文件夹 ：fmaszx
		#delete 文件夹：hwsukj
		if not files_list:
			return
		data = {
			'to':to,#ftp 文件ID 197173
			'auth[]':[ file_id for file_id in files_list],
			}

		url = 'http://uploaded.net/api/file/move'
		try:
			r = self.r_session.post(url=url,data=data, allow_redirects=True)
			print r.text
		except Exception as e:
			raise e

	def update_urls(self):
		self.login()
		json_data = self.get_new_uploaded_file_url()
		self.para_new_url(json_data=json_data)

class GrabNewODL_SH():
	'''
	抓取新的下载地址
	'''
	def __init__(self):
		self.data = {
		'login': 'nlxl001',
		'loginFormSubmit': 'Login',
		'op': 'login',
		'password': '123qwe',
		'redirect': 'http://ryushare.com/'

		}

		self.headers = {

		'POST': '/ HTTP/1.1',
		'Host': 'ryushare.com',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
		'Accept-Encoding': 'gzip, deflate',
		'Referer': 'http://ryushare.com/login.html',
		'Cookie': 'aff2=0; __utma=21463736.2104919758.1418543060.1418543060.1418549388.2; __utmc=21463736; __utmz=21463736.1418543060.1.1.utmcsr=filmav.com|utmccn=(referral)|utmcmd=referral|utmcct=/56602.html; login=nlxl001; xfss=; __utmb=21463736.5.10.1418549388; __utmt=1',
		'Connection': 'keep-alive',


		}
		self.url = 'http://ryushare.com/'
		self.url_filesystem = 'http://ryushare.com/?op=my_files'
		self.r_session = requests.session()
		self.try_download_count = 0
		self.total_size = 0
		self.logining = False
		self.dir_delete = '95579'
		self.dir_done = '95578'
		#done 文件夹 ：fmaszx
		#delete 文件夹：hwsukj
	def login(self):
		self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.logining = True



	def get_new_uploaded_file_url(self):
		'''
		'''
		url = 'http://ryushare.com/?op=my_files&fld_id=0'
		files = []
		r = self.r_session.get(url=url, allow_redirects=True)
		h = pq(r.text)
		trs = h('tr[align="center"]').items()
		for tr in trs:
			tr = pq(tr)
			url = tr('td[align="left"]')('a').attr('href')
			file_id = tr('input[name="file_id"]').attr('value')
			file_name = tr('td[align="left"]')('a').text()
			size_in_view = tr('td[align="right"]').text()
			# print file_id
			# print file_name
			# print size_in_view
			# print url
			files.append({
				'url':url,
				'file_id':file_id,
				'file_name':file_name,
				'size_in_view':size_in_view,
			})
		return files


	def para_new_url(self,files={}):
		db_session = create_session()
		# json_data = json.loads(json_data)
		file_ids = []
		file_ids_deleted = []

		for file in files:
			file_name = file.get('file_name')
			file_size_in_view = file.get('size_in_view')
			file_id = file.get('file_id')
			url = file.get('url')


			ndl_inst = db_session.query(NewDownloadLink).filter_by(file_name=file_name,url_type='ryushare.com').first()
			if ndl_inst is not None:
				# 正确的文件大小
				right_size_in_view = humanize.naturalsize(ndl_inst.file_size,gnu=True,format='%f')
				# 只需要数字部分
				right_size_in_view = re.sub('[a-zA-Z ]','',right_size_in_view)
				file_size_in_view = re.sub('[a-zA-Z ]','',file_size_in_view)

				if float(right_size_in_view) == float(file_size_in_view):
					#如果url抓取失败，或者没有得到正确的url，url仍旧保持为文件名，所以，http没有在包含在url（用作判断条件）
					ndl_inst.url = url
					ndl_inst.file_size_in_view = file_size_in_view
					db_session.add(ndl_inst)
					db_session.commit()
					file_ids.append(file_id)
					Msg = '更新%s 的新URL' % file_name.encode('utf8')
					wp_logging(Msg=Msg)
				else:#大小不相等，属于上传失败的文件，删除！
					file_ids_deleted.append(file_id)



		db_session.close()
		#none 和不相等的移动到delete_dir_id
		self.move_files_to_dir(files_list=file_ids_deleted, to_folder=self.dir_delete)
		#已经更新的移动到done dir
		self.move_files_to_dir(files_list=file_ids, to_folder=self.dir_done)


	def move_files_to_dir(self,files_list=[], to_folder='',):

		if not files_list:
			return
		data = {
			'create_new_folder': '',
			'file_id': [ file_id for file_id in files_list],
			'fld_id': '0',
			'key': '',
			'op': 'my_files',
			'to_folder': to_folder,
			'to_folder_move': 'Move files',

			}

		url = 'http://ryushare.com/'
		try:
			r = self.r_session.post(url=url,data=data, allow_redirects=True)
			# print r.text
		except Exception as e:
			raise e

	def update_urls(self):
		self.login()
		files = self.get_new_uploaded_file_url()
		self.para_new_url(files=files)
#
# grab_new_odl = GrabNewODL()
if __name__ == '__main__':

	# grab_new_odl.login()
	# grab_new_odl.download()
	# grab_new_odl.grab_ndls()
	# grab_new_odl.get_1000()
	# grab_new_odl.move_files_to_dir()
	# grab_new_odl.get_new_uploaded_file_url()
	# names = common_utility.get_files_in_dir('/home/l/app/learning/wangpan/wp_resource/articles_file/1/unrared_files')
	# print names

	# upnet = GrabNewODL_UPNET()
	# upnet.login()
	# upnet.move_files_to_dir(files_list=['9lr16lec','r37668ch'] ,to=upnet.dir_done)
	#
	sh = GrabNewODL_SH()
	sh.login()
	sh.update_urls()
	# sh.get_new_uploaded_file_url()
	# sh.move_files_to_dir(files_list=[1611061,1611055],to_folder=sh.dir_done)
	# sh.move_files_to_dir(files_list=['9lr16lec','r37668ch'] ,to=upnet.dir_done)