# -*- coding: utf-8 -*-
#-v10m 分卷大小1m , -ep 表示：不要把文件的路径层也照样复制进去
import subprocess, threading
import os
import shutil
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

seeds_wait_rar = os.path.dirname(os.path.abspath(__file__)) + '/seeds_wait_rar/'
seeds_uploaded = os.path.dirname(os.path.abspath(__file__)) + '/seeds_uploaded/'
seeds_rared = os.path.dirname(os.path.abspath(__file__)) + '/seeds_rared/'

file_names = os.listdir(seeds_wait_rar)
for file_name in file_names:
	file_name = file_name.decode('utf-8')

	file_name_no_suffix = file_name.split('.torrent')[0].replace(' ','_')+'.rar'
	file_name = file_name.replace(' ','\ ') # shell 要求给空格加上转换符
	file_name_rared = seeds_wait_rar+file_name_no_suffix

	seed_path = seeds_wait_rar + file_name
	attachment_path = os.path.dirname(os.path.abspath(__file__)) + u'/desktop_wallpaper.jpg'
	if os.path.exists(file_name_rared + '.rar'):
		continue

	cmd = u'/usr/bin/rar a -m0 -ep ' + file_name_rared +' '+ seed_path
	cmd += " "+ attachment_path
	command = ShellCommand(cmd)
	result_dic = command.run(timeout=10)
	if result_dic.get('status') == 0:
		Msg = u'%s 压缩成功!' % file_name
		print Msg
	elif result_dic.get('status') == 'Time Out':
		Msg = u'%s 压缩超时!' % file_name
		print Msg
	else:
		raise Exception,'压缩发生为止错误：%s ' % result_dic.get('status')

	seeds_rared_dir = '/home/admin/lin2.sborg.in/public_html/myfiles/filmav/seeds_rared/'
	if not os.path.exists(seeds_rared_dir):
		os.makedirs(seeds_rared_dir)
	try:
		shutil.move(seed_path,seeds_uploaded)
		shutil.move(file_name_rared,seeds_rared_dir)
	except Exception as e:
		os.remove(seed_path)
		os.remove(file_name_rared)
		print e


