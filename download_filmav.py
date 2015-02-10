# -*- coding: utf-8 -*-
import logging
import os
import requests
# CHUNK_SIZE = 8192
# CHUNK_SIZE = 10485760 #10M
# CHUNK_SIZE = 5242880 # 5M
import threading
import time
from datetime import date

CHUNK_SIZE = 10485760 # 5M
import sys
reload(sys)
sys.setdefaultencoding('utf8')
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
		self.dir_path = '' #硬编码地址
		self.downloading_amount = 0
		self.urls_downloaded_amount = 0 # 已下载文件统计
		self.urls_amount = 0 # 待下载的文件数

	def login(self):
		self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.logining = True

	def get_urls(self):

		# #todo 从github 获取待下载的url文件 ：download_urls.txt
		# link = u'https://raw.githubusercontent.com/lotaku/wp_sys/develop/download_urls.txt'
		# try:
		# 	file = self.r_session.get(link, stream=True, allow_redirects=True)
		# except requests.exceptions.Timeout as e:
		# 	Msg = e + u'获取urls列表文件失败 Download Time out'
		# 	print Msg
		# 	return
		# print 'connect to download_urls.txt'
		# with open('download_urls.txt', 'wb') as local_file:
		# 	for content in file.iter_content(1024):
		# 		if content:  # filter out keep-alive new chunks
		# 			local_file.write(content)
		# 			local_file.flush()

		#todo 从文件读取下载地址，存入一个列表

		url_list = []
		with open('download_urls.txt','r') as f:
			for line in f.readlines():
				url_list.append(line.rstrip())
		# print url_list
		return url_list

	def run(self):
		self.login()
		url_list = self.get_urls()
		self.urls_amount = len(url_list)
		while True:
			if not url_list:
				Msg = u'waiting list is empty'
				print Msg
				return
			if self.downloading_amount < 5:
				url = url_list.pop()
				check_downloaded = threading.Thread(target=self.download, args=(url.strip(),))
				check_downloaded.start()
				self.downloading_amount += 1
			time.sleep(1)
		print u'urls_amount:           %s' % self.urls_amount
		print u'urls_downloaded_amount:%s' % self.urls_downloaded_amount
	def download(self,url):
		'''
		用requests下载
		'''
		file_name=url.split('/')[-1]
		dir_name = file_name.split('.')[0]


		file_dir = '/home/admin/lin2.sborg.in/public_html/myfiles/filmav/'+dir_name +'/'
		# file_dir = '/home/admin/lin2.sborg.in/public_html/myfiles/filmav/'+str(date.today()) +'/'
		file_path = file_dir+file_name
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)

		file_size_dl = 0

		# todo 下载是有效的下载方法，可以增大chunk_size

		try:
			file = self.r_session.get(url, stream=True, allow_redirects=True)
			# file = self.r_session.post(url_inst.url, data = {'stream':True, 'allow_redirects':True})
		except requests.exceptions.Timeout as e:
			Msg = e
			print Msg
			self.downloading_amount -= 1
			return 'Download Time out'
		self.total_size = int(file.headers['content-length'])

		#todo 判断文件是否已经存在，并且大小是否正确，
		#如果存在，大小正确，直接return
		#如果存在，大小不正确，删除文件，重新下载
		if os.path.exists(file_path):
			if os.path.getsize(file_path) ==self.total_size:
				Msg = u'already downloaded and complete!'
				# print Msg
				self.downloading_amount -= 1
				return
			Msg = u'file is exist,but it\'s size is not correct.'
			print Msg
			os.remove(file_path)
		print u'prepare to download：%s' % file_name.encode('utf8')
		with open(file_path, 'wb') as local_file:
			# for content in file.iter_content(CHUNK_SIZE):
			for content in file.iter_content(CHUNK_SIZE):
				if content:  # filter out keep-alive new chunks
					file_size_dl += len(content)
					local_file.write(content)
					local_file.flush()
					completeness = u"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / self.total_size)
					# completeness = completeness + chr(8)*(len(completeness)+1)
					Msg = u'{completeness}  {file_name}'\
						.format(file_name=file_name, completeness=completeness)
					print Msg
		self.downloading_amount -= 1
		if file_size_dl == self.total_size:
			print 'Download successful'
			return
		else:
			print 'Download fail'
			return


download_sys = GrabNewODL()
# download_sys.login()
download_sys.run()