# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
from sqlalchemy import exc
import logging
import logging.config
from contextlib import closing
from settings import CHUNK_SIZE,IMG_PATH
from settings import DB_ENGINE, DB_BASE,logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
#数据库表
from models import FileLink, Article,Image,OldDownloadLink,NewDownloadLink,Tag

from utility import create_session, wp_logging


import os

# logging.config.fileConfig("/home/l/app/learning/wangpan/logging.conf")
# logger = logging.getLogger("wp")

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
		self.website = 'filmav.com'
		#引入数据库表
		self.FileLink = FileLink # 表：用于保存文章链接

		# self.db_session = None
		self.uploadable_headers = {
				'Request URL': 'http://www.uploadable.ch/login.php',
				'Accept-Encoding': 'gzip,deflate,sdch',
				'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.',
				'Connection': 'keep-alive',
				'Host': 'www.uploadable.ch',
				'Referer': 'http://www.uploadable.ch/login.php',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
			}
		self.article_files = {}

	def db_session(self):
		db_session = create_session(DB_ENGINE, DB_BASE)
		return db_session


	def get(self,url):
		try:
			self.r = self.requests.get(url,headers = self.headers)
			logging.debug('获取网页成功')

		except Exception ,e:
			Msg = '获取网页失败，原因：%s' % e
			logging.debug(Msg)

		return self.r

	def get_image(self,url):
		r = self.get(url=url)
		if r.status_code is not 200:
			logging.debug('获取网页失败，无法进一步抓取图片')
			return
		whole_html = pq(self.r.text)
		body = whole_html('.entry')
		body_str =str(unicode(body).encode('utf-8'))

		#抓取所有图片,使用非贪婪模式
		small_img_re_str = r'(?P<images>http://img[\d]{0,3}.imagetwist.com/.*?.jpg)'
		small_img_re = re.compile(small_img_re_str)
		small_imgs = re.findall(small_img_re, body_str)
		for small_img in small_imgs:
			"""
			small_path--> 图片存于small_path, 图片存于big_path-->图片存于big_path
			"""

			big_img, img_type = self.get_big_img_and_type(small_img=small_img)
			#保存 small_path 图片
			self.save_image(url=small_img, img_type=img_type, path='small_path')
			self.save_image(url=big_img, img_type=img_type, path='big_path')

	def save_image(self,url,img_type='normal',path='small_path'):
		img_filename = url.split('/')[-1]
		img_filename = path + '_' + img_filename #区分大小图
		try:
			with closing(requests.get(url, stream=True)) as img:

				if img.status_code == 200:
					Msg = '抓取图片成功，开始下载...'
					print Msg
					logging.debug(Msg)
				else:
					Msg = "抓取图片失败，原因：%s " % img.status_code
					print Msg
					logging.debug(Msg)
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
							Msg =  '{0}% 已下载 --（图片名：{1})'.format(percent_completeness,img_filename)
							print Msg
							logging.debug(Msg)
						else:
							Msg =  '100% 已下载 --（图片名：{1})'.format(img_filename)
							print Msg
							logging.debug(Msg)

		except Exception ,e:
			Msg = "下载图片失败，原因：%s " % e
			print Msg
			logging.debug(Msg)

	def get_big_img_and_type(self, small_img):
		"""返回大图地址，已经原图类型（main，normal）"""
		img_type = 'main' #默认设定原图是主图
		#th替换成i
		big_img_re_str = r'/th/'
		big_img_re =re.compile(big_img_re_str)
		big_img = re.sub(big_img_re,'/i/',small_img)

		response = requests.get(big_img)
		print response.headers['content-length']
		if int(response.headers['content-length']) == 8183: #一张错误图片，则原图是normal图片
			img_type = 'normal'
			#将 jpg替换成 jpeg
			big_img_re_str = r'jpg$'
			big_img_re =re.compile(big_img_re_str)
			big_img = re.sub(big_img_re,'jpeg',big_img)
			print big_img
		return (big_img, img_type)





	def grab_article_url(self,website_index="http://filmav.com/"):
		"""
		抓取首页每篇文章链接

		"""
		#todo 循环各个页面，具体抓取文章内容时，记得根据文章链接最后数字进行排序，另，判断是否有有效的下载地址。

		r = requests.get(url=website_index, headers=self.headers)

		if r.status_code is not 200:
			Msg = "首页抓取不是200,返回状态码：" + str(r.status_code)
			print Msg
			logging.debug(Msg)
			return

		h = pq(r.text)
		article_urls_htmlelements = h('.more-link')
		article_urls=[]
		for url in article_urls_htmlelements:
			u = url.attrib['href'].split("#")[0]
			article_urls.append(u)

		return article_urls


	def grab_article_body(self,url='http://filmav.com/53769.html'):

		r = requests.get(url=url, headers=self.headers)

		if r.status_code is not 200:
			Msg = "首页抓取不是200,返回状态码：" + str(r.status_code)
			wp_logging(Msg=Msg)
			return

		h = pq(r.content)
		body = h('.entry')
		#匹配中文，记得要进行编码
		old_body_str =str(unicode(body).encode('utf-8'))

		#抓取主体
		old_body = re.split('<span style="color: #ff0000;"><strong>Premium Dowload ゴッド会員 高速ダウンロード</strong></span><br />',old_body_str)
		old_body = old_body[0][:-53]

		#抓取文章标题
		title = h('.title-single')
		if len(title.html()) < 0:
			Msg = "失败! 抓取文章标题!"
			wp_logging(Msg=Msg)
			return
		self.article_files.update(
			title = title
		)
		Msg = "抓取文章标题：" + str(unicode(title.html()).encode('utf-8'))
		wp_logging(Msg=Msg)
		#todo 抓取作者，电影分类
		#抓取电影分类
		categories = h('a[rel="category tag"]')
		for category in categories:
			Msg = "抓取文章分类：" + category.text
			wp_logging(Msg=Msg)
		#抓取tag,使用非贪婪模式
		tags_re_str = r'tag/.*?>(.*?)</a>'
		tags_re = re.compile(tags_re_str)
		tags = re.findall(tags_re, old_body_str)
		for tag in tags:
			Msg = "抓取文章标签：" + tag
			wp_logging(Msg=Msg)

		#抓取old_download_links
		links_re_str = r'(http://www.uploadable.ch/file/.*?)["<]'
		links_re = re.compile(links_re_str)
		links = re.findall(links_re, old_body_str)
		for link in links:
			print "old download links:",link

		#抓取文件名
		file_name=''
		file_name_re_strs  = [r'>(.*?).part\d.rar',r'/?([\d\w]*[-]*[\w\d]*)\.wmv']
		for file_name_re_str in file_name_re_strs:
			file_name_re = re.compile(file_name_re_str)
			file_names = re.findall(file_name_re, old_body_str)
			if len(file_names) == 0:
				continue
			for file_name_ in file_names:
				file_name = file_name_
				Msg =  "抓取文件名： "+ file_name
				wp_logging(Msg=Msg)
				break
		# 创建 文章实例
		if len(file_name):
			self.article_files.update(
				file_name = file_name,
				website = self.website,
				title = ''
			)
			new_article = Article(file_name=file_name)
			Msg =  "创建文章实例： "+ new_article.file_name
			wp_logging(Msg=Msg)



	def save_article_url(self, article_urls):
		db_session = self.db_session()
		model_url = self.FileLink
		for url in article_urls:
			url_instance = model_url(url=url,website=self.website)
			db_session.add(url_instance)
			try:
				db_session.commit()
				Msg =  "已保存文件链接： "+url
				logging.debug(Msg)
			except exc.IntegrityError, e :
				Msg =  "捕获异常(链接已经存在）： "+e.message
				logging.debug(Msg)
				db_session.close()

	# def grap_atrical_details(self):

if __name__ == '__main__':
	filmav_grab = Filmav_Grab()
	# filmav_grab.get(url='http://filmav.com/53049.html')
	# filmav_grab.get_image(url='http://filmav.com/52792.html')
	# article_urls = filmav_grab.grab_article_url()
	# filmav_grab.save_article_url(article_urls)
	filmav_grab.grab_article_body()



