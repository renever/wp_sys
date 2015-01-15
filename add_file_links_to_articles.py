# -*- coding: utf-8 -*-
import os
from datetime import date
import json
import time

import codecs
dir = os.path.dirname(os.path.abspath(__file__))+'/articles/filmav/grabed_articles/'
download_link_file = os.path.dirname(os.path.abspath(__file__))+'/articles/filmav/' + '%s_download_links.txt' % str(date.today()).replace('-','_')
print download_link_file
#把新的下载地址转成一个字典
up_download_links = {}
rg_download_links = {}
with open(download_link_file) as f:
	for line in f.readlines():
		up_links = []
		rg_links = []
		file_name = line.split('/')[-1].split('.')[0]
		if u'rapidgator' in line:
			rg_download_links.setdefault(file_name,[]).append(line.strip('\n'))
		else:
			up_download_links.setdefault(file_name,[]).append(line.strip('\n'))



	print up_download_links
	print rg_download_links
#
for id in os.listdir(dir):
	# if id != '60667.py':
	# 	continue

	file_path = dir + id

	print 'id: %s ' % id

	with codecs.open(file_path,encoding='UTF-8') as f:
		dict = json.load(f)
		file_name = dict['file_name'].split('.')[0]
		if not up_download_links.has_key(file_name):
			continue
		dict.update({'uploaded_net':up_download_links[file_name]})
		dict.update({'rapidgator':rg_download_links[file_name]})

	with codecs.open(file_path,'wb',encoding='UTF-8') as f:
		json.dump(dict, f)



