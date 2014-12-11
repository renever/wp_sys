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
# r_session = requests.session()
# r_session
# 替换主体内容
content = u'''<p>xxx-av 21708  Wデカパイコラボ 2
<span class="wp_keywordlink_affiliate"><a href="http://filmav.com/tag/%e8%91%89%e5%b1%b1%e3%81%8f%e3%81%bf%e3%81%93" title="View all posts in 葉山くみこ" target="_blank">葉山くみこ</a></span>
<span class="wp_keywordlink_affiliate"><a href="http://filmav.com/tag/%e5%92%b2%e6%9c%88%e7%be%8e%e7%be%bd" title="View all posts in 咲月美羽" target="_blank">咲月美羽</a></span>
<br />
<a href="http://imagetwist.com/us8j8q1tvvvf/movie_main.jpg.html" target="_blank" class="external" rel="nofollow"><img src="http://img106.imagetwist.com/th/07415/us8j8q1tvvvf.jpg" border="0" /></a>
<br />
     まさに夢のコラボレーション第二弾！ 巨乳ギャルにパイズリ生中出し！
     <span class="wp_keywordlink_affiliate"><a href="http://filmav.com/tag/%e8%91%89%e5%b1%b1%e3%81%8f%e3%81%bf%e3%81%93" title="View all posts in 葉山くみこ" target="_blank">葉山くみこ</a></span>、
     <span class="wp_keywordlink_affiliate"><a href="http://filmav.com/tag/%e5%92%b2%e6%9c%88%e7%be%8e%e7%be%bd" title="View all posts in 咲月美羽" target="_blank">咲月美羽</a></span>
     ちゃんの爆乳コンビが繰り広げる迫力満点の激エロ作品。 圧巻のパイズリに乳を上下に大きく揺らして絶叫ピストン。 中出しされたザーメンがあふれ出る様は卑猥で猥褻！ 男を狂わす卑猥ボディ！ オナニーしているところを見られ、オマンコ指ホジにイラマチオ！ 次は男にベッドでオナニー披露。 ネットリ愛撫でガッツリ中出し！ 巨乳美女の胸にたっぷり埋もれちゃってください！
     <br />
<a href="http://www.allanalpass.com/Avre2" target="_blank" class="external" rel="nofollow"><img src="http://img57.imagetwist.com/th/07415/bzbyvl63cpet.jpg" border="0" /></a><br />
<strong><span id="more-55864"></span></strong><br />
'''
h = pq(content)
a_list = h("span[class='wp_keywordlink_affiliate']")("a")
for a in a_list:
	print a.text