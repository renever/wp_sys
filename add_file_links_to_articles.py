# -*- coding: utf-8 -*-
import os
from datetime import date
import json
dir = os.path.dirname(os.path.abspath(__file__))+'/articles/filmav/'+str(date.today())+'/'
for file_name in os.listdir(dir):
	# print file_name
	#10mu_011415_01_fhd.py
	if file_name != '10mu_011415_01_fhd.py':
		continue
	# article_dict = file_name.split('.')[0]
	file_path = dir + file_name
	print file_path
	dict = json.load(file_path)
	print dict

