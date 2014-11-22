# - * - coding:utf-8 - * -
from __future__ import division
import os
import ftplib
from ftplib import FTP
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import time
class MyFtp():

	def __init__(self,host='ftp.uploadable.ch',user='lxl001',password='f19174de',port=21,blocksize=8192):
		self.host = host
		self.user = user
		self.password = password
		self.port = port
		self.ftp=FTP(host)
		self.blocksize = blocksize

	def login(self):
		self.ftp.login(user=self.user, passwd=self.password)


	def handle(self):

		pass

	def upload_list(self,full_path_file_names):

		for full_path_file_name in full_path_file_names:
			file_name = os.path.basename(full_path_file_name)
			with open(full_path_file_name,'rb') as f:
				try:
					myFtp.ftp.storbinary('STOR ' + file_name,
							   f,
							   self.blocksize,
							   self.callback_handle(file_name))
				except ftplib.error_perm :
					print "上传失败！"
				print "%s 上传成功。" % file_name

	def upload(self,full_path_file_name):
		# sizeWritten = 0
		# blocksize = 1024
		# file_name = '123.pdf'
		# file_total_size = os.path.getsize(file_name)
		# print 'file_total_size: %s' % file_total_size
		# def handle(block):
		# 	global sizeWritten
		# 	sizeWritten += blocksize
		# 	result = sizeWritten / file_total_size * 100
		# 	print "%0.3f percent complete" % result
		new_ftp = MyFtp()
		new_ftp.login()

		file_name = os.path.basename(full_path_file_name)
		with open(full_path_file_name,'rb') as f:
			try:
				new_ftp.ftp.storbinary('STOR ' + file_name,
						   f,
						   self.blocksize,
						   self.callback_handle(file_name))

			except ftplib.error_perm :
				print "上传失败！"
			print "%s 上传成功。" % file_name

	def callback_handle(self,file_name):
		print "%s 上传中..." % file_name
	def upload_thread(self):
		# Make the Pool of workers
		pass


class MyFile():
	def __init__(self,fileName=''):
		self.Name = fileName
		self.sizeWritten = 0
		self.total_size = 0
		self.pull_path = ''

	def close(self):
		pass


def get_all_file_path(base_file_dir=''):
	file_name_list = os.listdir(BASE_FILE_DIR)
	full_path_file_name_list = []
	for file_name in file_name_list:
		full_path_file_name = os.path.join(BASE_FILE_DIR,file_name)
		full_path_file_name_list.append(full_path_file_name)
	return full_path_file_name_list

# BASE_FILE_DIR = '/home/l/test1/'
BASE_FILE_DIR = '/home/l/temp'
ftp_host = 'ftp.uploadable.ch'
ftp_user = 'lxl001'
ftp_password = 'f19174de'

if __name__ == '__main__':
	full_path_file_name_list = get_all_file_path(BASE_FILE_DIR)

	myFtp = MyFtp()
	myFtp.login()


	pool = ThreadPool(10)

	results = pool.map(myFtp.upload, full_path_file_name_list)

	pool.close()
	pool.join()

