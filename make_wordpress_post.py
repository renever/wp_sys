# -*- coding: utf-8 -*-
import os
from datetime import date
import json
import time

import codecs
dir = os.path.dirname(os.path.abspath(__file__))+'/articles/filmav/grabed_articles/'

for id in os.listdir(dir):
	file_path = dir + id
	with codecs.open(file_path,encoding='UTF-8') as f:
		dict = json.load(f)
		file_name = dict['file_name'].split('.')[0]
		if not dict.has_key('uploaded_net'):
			continue
		print 'id: %s ' % id
		# print dict['uploaded_net']




