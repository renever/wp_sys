# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
from sqlalchemy import exc
import logging
import logging.config
from contextlib import closing
from settings import CHUNK_SIZE,IMG_PATH

import os

logging.config.fileConfig("/home/l/app/learning/wangpan/logging.conf")
logger = logging.getLogger("wp")

class Filmav_Grab():

	def __init__(self):
		self.headers = {
			'Host': 'filmav.com',
			'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
			'Accept-Encoding': 'gzip, deflate',
			'Connection': 'keep-alive',
			}
		self.requests = requests
		self.r = '' # 用于保存抓取网页的Response


	def get(self,url):
		try:
			self.r = self.requests.get(url,headers = self.headers)
			logging.debug('获取网页成功')

		except Exception ,e:
			Mes = '获取网页失败，原因：%s' % e
			logging.debug(Mes)

	def get_image(self,url):
		self.get(url=url)
		if self.r.status_code is not 200:
			logging.debug('获取网页失败，无法进一步抓取图片')
			return
		whole_html = pq(self.r.text)
		body = whole_html('.entry')
		body_str =str(unicode(body).encode('utf-8'))
		# src="http://img58.imagetwist.com/th/07136/5d5ks9fozzp8.jpg

		#抓取所有图片,使用非贪婪模式
		images_re_str = r'(?P<images>http://img[\d]{0,3}.imagetwist.com/.*?.jpg)'
		images_re = re.compile(images_re_str)
		images = re.findall(images_re, body_str)
		for image in images:
			# print "images links:",image
			#todo 以上获得所有小图，th 字眼在链接里，替换i，获得大图，下载图片失败，将jpg换成jpeg
			self.save_image(url=image)
	def save_image(self,url):
		img_filename = url.split('/')[-1]
		try:
			with closing(requests.get(url, stream=True)) as img:

				if img.status_code == 200:
					logging.debug('抓取图片成功，开始下载...')
				else:
					Mes = "抓取图片失败，原因：%s " % img.status_code
					logging.debug(Mes)
					return

				file_total_size = img.headers.get('content-length')
				img_new_path = os.path.join(IMG_PATH,img_filename)
				#todo 判断图片是否存在。存在，则名字加上时间戳
				with open(img_new_path, 'wb') as f:
					for counter,chunk in enumerate(img.iter_content(chunk_size=CHUNK_SIZE)):
						if chunk:  # filter out keep-alive new chunks
							f.write(chunk)
							f.flush()
							percent_completeness = 100*counter*CHUNK_SIZE/int(file_total_size)
							Mes =  '{0}% 已下载 --（图片名：{1})'.format(percent_completeness,img_filename)
							logging.debug(Mes)
						else:
							Mes =  '100% 已下载 --（图片名：{1})'.format(img_filename)
							logging.debug(Mes)

		except Exception ,e:
			Mes = "抓取图片失败，原因：%s " % e
			logging.debug(Mes)







def filmav_grab_article_url(website_index="http://filmav.com/"):
	headers={
		'Host': 'filmav.com',
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
		'Accept-Encoding': 'gzip, deflate',
		'Connection': 'keep-alive',
	}


	r = requests.get(url=website_index, headers=headers)

	if r.status_code is not 200:
		s = "首页抓取不是200,返回状态码：" + str(r.status_code)
		print s
		return s

	h = pq(r.text)
	article_urls_htmlelements = h('.more-link')
	article_urls=[]
	for url in article_urls_htmlelements:
		u = url.attrib['href'].split("#")[0]
		article_urls.append(u)

	return article_urls

# def filmav_grab_article_body(url='http://filmav.com/52707.html'):
def filmav_grab_article_body(url='http://filmav.com/52686.html'):
	headers={
		'Host': 'filmav.com',
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
		'Accept-Encoding': 'gzip, deflate',
		'Connection': 'keep-alive',
	}

	r = requests.get(url=url, headers=headers)

	if r.status_code is not 200:
		s = "首页抓取不是200,返回状态码：" + str(r.status_code)
		print s
		return s

	h = pq(r.text)
	body = h('.entry')
	#匹配中文，记得要进行编码
	str1 =str(unicode(body).encode('utf-8'))
	# print str1

	#抓取主体
	newbody = re.split('<span style="color: #ff0000;"><strong>Premium Dowload ゴッド会員 高速ダウンロード</strong></span><br />',str1)
	newbody = newbody[0][:-53]

	#抓取tag,使用非贪婪模式
	tags_re_str = r'tag/.*?>(.*?)</a>'
	tags_re = re.compile(tags_re_str)
	tags = re.findall(tags_re, str1)
	# for tag in tags:
	# 	print tag

	#抓取old_download_links
	links_re_str = r'(http://www.uploadable.ch/file/.*?)["<]'
	links_re = re.compile(links_re_str)
	links = re.findall(links_re, str1)
	for link in links:
		print "old download links:",link


	#抓取文件名
	file_name_re_strs  = [r'>(.*?).part\d.rar',r'/?([\d\w]*[-]*[\w\d]*)\.wmv']
	for file_name_re_str in file_name_re_strs:
		file_name_re = re.compile(file_name_re_str)
		file_names = re.findall(file_name_re, str1)
		if len(file_names) == 0:
			continue
		for file_name in file_names:
			print "file_name: ",file_name

		break


def filmav_grab_article_image(url='http://filmav.com/53026.html'):
	headers={
		'Host': 'filmav.com',
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
		'Accept-Encoding': 'gzip, deflate',
		'Connection': 'keep-alive',
	}

	r = requests.get(url=url, headers=headers)

	if r.status_code is not 200:
		s = "首页抓取不是200,返回状态码：" + str(r.status_code)
		print s
		return s

	h = pq(r.text)
	body = h('.entry')
	#匹配中文，记得要进行编码
	str1 =str(unicode(body).encode('utf-8'))





def filmav_save_article_url(article_urls,session,model_url):
	website = 'filmav.com'
	for url in article_urls:
		url_instance = model_url(url=url,website=website)
		session.add(url_instance)
		try:
			session.commit()
		except exc.IntegrityError, e :
			print "捕获异常(链接已经存在）： "+e.message
			session.close()


if __name__ == '__main__':
	filmav_grab = Filmav_Grab()
	# filmav_grab.get(url='http://filmav.com/53049.html')
	filmav_grab.get_image(url='http://filmav.com/52792.html')



