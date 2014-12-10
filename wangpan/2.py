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
# url = 'http://filmav.com/55779.html'
# r = requests.get(url)
# h = pq(r.content)
# post_time = h('.post-info-date').text()
# print post_time
# list = re.split(',| ',post_time)
# print list
#
# t_str = list[-4][:3] +' '+ list[-3] + ' ' + list[-1]
# t = datetime.strptime(t_str, '%b %d %Y')
# print t

#t2 = datetime.strftime(datetime.now(),'%b %d %Y' )
#print t2
##print datetime.now()
#img = 'http://img106.imagetwist.com/i/07400/09rfk51yja42.jpg'
#print len(img)
#img_list = img.split('/')
#print img_list[-1]

# 抓取文件body内容
# url = 'http://filmav.com/52705.html'
# r = requests.get(url)
# h = pq(r.content)
# old_body_str = h('.entry').html()
# #抓取主体
# old_body = re.split(u'<span style="color: #ff0000;"><strong>Premium Dowload ゴッド会員 高速ダウンロード',old_body_str)
#
# # print old_body
# print 'old_body\'s type: %s' % type(old_body[0])
# print old_body[0]
# # print old_body[0]
# old_body = old_body[0]
# print "-"*99

#上传图片
r_session = requests.session()
r_session
