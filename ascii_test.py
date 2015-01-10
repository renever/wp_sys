# -*- coding: utf-8 -*-
import os
seeds_wait_rar = os.path.dirname(os.path.abspath(__file__)) + '/seeds_wait_rar/'
seeds_uploaded = os.path.dirname(os.path.abspath(__file__)) + '/seeds_uploaded/'
seeds_rared = os.path.dirname(os.path.abspath(__file__)) + '/seeds_rared/'

file_names = os.listdir(seeds_wait_rar)
for file_name in file_names:
	print file_name
	print u'' + file_name.decode('utf-8')