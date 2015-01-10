# -*- coding: utf-8 -*-
import os
import shutil
seeds_wait_rar = os.path.dirname(os.path.abspath(__file__)) + '/seeds_wait_rar/'
seeds_uploaded = os.path.dirname(os.path.abspath(__file__)) + '/seeds_uploaded/'
seeds_rared = os.path.dirname(os.path.abspath(__file__)) + '/seeds_rared/'

file_names = os.listdir(seeds_wait_rar)
for file_name in file_names:
	try:
		a =  u'' + file_name
	except Exception as e:
		print file_name
		print e

#todo 替换非unicode或会影响shell命令的符号
for file_name in os.listdir(seeds_wait_rar):
	new_file_name = file_name.replace(' ','_').replace("&amp;",'_').replace('[','_')\
							 .replace(']','_').replace('(','_').replace(')',"_").replace(':','_')
	file_name_path = seeds_wait_rar+'/'+ file_name
	new_file_name_path = seeds_wait_rar+'/'+ new_file_name

	os.rename(file_name_path,new_file_name_path)

