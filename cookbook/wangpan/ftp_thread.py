# - * - coding:utf-8 - * -
from __future__ import division
import os
from ftplib import FTP
class MyFtp():
	def __init__(self,host,user,password,port=21):
		self.host = host
		self.user = user
		self.password = password
		self.port = port
		self.ftp=FTP(host)

	def connent(self):
		self.ftp.login(host=self.host, user=self.user, password=self.password)

	def handle(self):
		pass

class MyFile():
	def __init__(self,fileName):
		self.Name = fileName
		self.file = open(fileName,'rb')
		self.sizeWritten = 0
		self.total_size = os.path.getsize(fileName)

	def close(self):
		self.file.close()
FILE_BASE_DIR = '/home/l/test1'

ftp_host = 'ftp.uploadable.ch'
ftp_user = 'lxl001'
ftp_password = 'f19174de'

files_list = os.listdir('/home/l/test1')
# print files_list
file_names = []
for file_name in files_list:
	full_file_name = os.path.join(FILE_BASE_DIR, file_name)
	file_names.append(full_file_name)
	# print os.path.basename(full_file_name)

myFtp = MyFtp(host=ftp_host,user=ftp_user,password=ftp_password)
myFtp.connent()

sizeWritten = 0
blocksize = 1024
file_name = '123.pdf'
file_total_size = os.path.getsize(file_name)
print 'file_total_size: %s' % file_total_size
def handle(block):
	global sizeWritten
	sizeWritten += blocksize
	result = sizeWritten / file_total_size * 100
	print "%0.3f percent complete" % result

with open(file_name,'rb') as f:

	myFtp.ftp.storbinary('STOR ' + file_name,\
				   f,\
				   blocksize,\
				   handle)