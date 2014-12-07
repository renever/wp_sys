# -*- coding: utf-8 -*-
#import os
#a = os.path.getsize('/home/l/app/learning/wangpan/wp_resource/articles_file/1/rared_files/chrome.part6.rar')
#print a
##import time
#from datetime import datetime

#os.environ['TZ'] = 'Asia/Shanghai'
#os.environ['TZ'] = 'US/Eastern'

#print datetime.now()
import requests
from pyquery import PyQuery as pq
import re
from datetime import datetime
url = 'http://filmav.com/55779.html'
r = requests.get(url)
h = pq(r.content)
post_time = h('.post-info-date').text()
print post_time
list = re.split(',| ',post_time)
print list

t_str = list[-4][:3] +' '+ list[-3] + ' ' + list[-1]
t = datetime.strptime(t_str, '%b %d %Y')
print t

#t2 = datetime.strftime(datetime.now(),'%b %d %Y' )
#print t2
##print datetime.now()
#img = 'http://img106.imagetwist.com/i/07400/09rfk51yja42.jpg'
#print len(img)
#img_list = img.split('/')
#print img_list[-1]


