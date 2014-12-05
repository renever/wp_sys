# -*- coding: utf-8 -*-
#第三方包
import requests
from pyquery import PyQuery as pq
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from sqlalchemy.sql import func
import humanize
#自定义settings
#-----线程池大小
from settings import SAVE_ARTICLE_URL_POOL_SIZE,GRAB_ARTICLE_URL_POOL_SIZE, GRAB_ARTICLES_POOL_SIZE
from settings import CHUNK_SIZE,IMG_PATH
from settings import DB_ENGINE, DB_BASE
#-----文件夹目录
from settings import DOWNLOAD_DIR, ARTICLE_FILES_DIR
#-----全局变量
from settings import DOWNLOAD_SYSTEM_IS_RUNNING
from settings import FILE_UNIT_CONVERSION
#数据库表
from models import FileLink, Article,Image,OldDownloadLink,NewDownloadLink,Tag, Category
from utility.common import create_session, wp_logging, get_or_create, FirefoxDriver, common_utility
from utility.common import ShellCommand, FilmAvFtp

import unicodedata
#系统包
import logging
import logging.config
from contextlib import closing
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import re
import time
import os
import thread
import threading
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

# logging.config.fileConfig("/home/l/app/learning/wangpan/logging.conf")
# logger = logging.getLogger("wp")
#已经在当前DB_SESSION 创建会更新的TAG
TAG_LIST_IN_DB_SESSION = []
CATEGORY_LIST_IN_DB_SESSION = []
WAITING_DOWNLOAD_LIST = [] #如果正在下载量少于10，并且该列表为空，则从数据库取得未下载的URL
WAITING_RAR_LIST = []
WAITING_UNRAR_LIST = []
WAITING_UPLOAD_LIST = []

DOWNLOADING_LIST = [] # 同时下载量5
RARING_LIST = [] #同时压缩数量 1 优先处理压缩，可以就接着上传
UNRARING_LIST = [] #同时解压数量 1
UPLOADING_LIST = []
#最大限制数
MAX_DOWNLOADING_NUMBER = 5
MAX_RAR_AND_UNRAR_NUMBER = 1
# MAX_UPLOAD_NUMBER = 1 # 一篇文章，一般有6个下载，在线网站下载速度一般10M/S
MAX_UPLOAD_NUMBER = 5
HAVE_UPLOAED_NUMBER = 0 #判断是否读取网页进行更新文章的新地址

#检索新上传链接条件
#是否为系统初次检索
GRAB_NEW_URL_FIRST = True
GRAB_NEW_URL = False # 当有文章上传成功时，就改为TRUE

class Filmav_Grab():

	def __init__(self):
		db_session = self.db_session()
		self.headers = {
			# 'Host': 'filmav.com',
			# 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
			# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			# 'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
			# 'Accept-Encoding': 'gzip, deflate',
			# 'Connection': 'keep-alive',
			'Host': 'filmav.com',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'zh-cn,en;q=0.7,en-us;q=0.3',
			'Accept-Encoding': 'gzip, deflate',
			'Referer': 'http://filmav.com/',
			'Cookie': 'HstCfa2322499=1413801408469; HstCla2322499=1416845473653; HstCmu2322499=1416643008866; HstPn2322499=12; HstPt2322499=155; HstCnv2322499=40; HstCns2322499=65',
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
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \(KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
		}
		self.article_files = {}
		#todo 暂时屏蔽 driver 的初始化
		self.driver = FirefoxDriver()

		self.driver_login_time = None
		self.global_db_session = db_session
		self.DOWNLOAD_SYSTEM_IS_RUNNING = False
		self.UNRAR_SYSTEM_IS_RUNNING = False
		self.RAR_SYSTEM_IS_RUNNING = False
		self.UPLOAD_SYSTEM_IS_RUNNING = False

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
							percent_completeness = 100*counter*CHUNK_SIZE/float(file_total_size)
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

	def grab_article_url(self,page_start=1,page_end=1):
		'''
		计算待抓取的所有页面，存在一个列表里，并传递给一个线程池
		'''
		page_number_list = [page_number for page_number in range(page_start,page_end+1)]

		#同时抓取多少网页的文章URL
		pool = ThreadPool(GRAB_ARTICLE_URL_POOL_SIZE)
		try:
			pool.map(self.grab_article_url_of_per_page, page_number_list)
		except Exception,e:
			Msg = '开始新线程报错：%s' % e
			wp_logging(Msg=Msg,allow_print=True)

	def grab_article_url_of_per_page(self,page_number):
		"""
		抓取首页每篇文章链接
		"""
		#todo 抓取制定页面范围的所有文件的链接。
		#todo 循环各个页面，具体抓取文章内容时，记得根据文章链接最后数字进行排序，另，判断是否有有效的下载地址。
		base_url = 'http://filmav.com/page/'
		article_urls = []
		# is_increased =None
		# for page_number in range(page_start,page_end+1):
		url = base_url + str(page_number)
		r = None
		try:
			r = requests.get(url=url, headers=self.headers)
		except Exception,e:
			Msg = '链接到网页失败：%s ' % e
			wp_logging(Msg=Msg)
			return


		if r.status_code is not 200:
			Msg = "首页抓取不是200,返回状态码：" + str(r.status_code)
			print Msg
			logging.debug(Msg)
			return

		h = pq(r.text)
		article_urls_htmlelements = h('.more-link')

		for article_url in article_urls_htmlelements:
			article_url_ = article_url.attrib['href'].split("#")[0]
			article_urls.append(article_url_)
		# 如果首页有更新，继续抓取下一页，看看是否更新了更多文章。
		# is_increased = self.save_article_url(article_urls)
		pool = ThreadPool(SAVE_ARTICLE_URL_POOL_SIZE)
		try:
			pool.map(self.save_article_url, article_urls)
		except Exception,e:
			Msg = '开始新线程报错：%s' % e
			wp_logging(Msg=Msg,allow_print=True)



		# if is_increased:
		# 	continue
		# else:
		# 	break

		# return article_urls

	def save_article_url(self, article_url):
		db_session = self.db_session()
		# is_increased = None
		# pre_filelinks_count = db_session.query(FileLink.id).count()
		# for url in article_url:
		url_instance,created = get_or_create(session=db_session, is_global=True, model=FileLink,url=article_url,website=self.website)
		if created:
			try:
				db_session.add(url_instance)
				db_session.commit()
				Msg =  "save article url ： " + article_url
				wp_logging(Msg=Msg, allow_print=True)

			except exc.IntegrityError, e :
				Msg =  "save article url fail： " + e.message
				wp_logging(Msg=Msg, allow_print=False)
				#如果db_session.commit() 出现异常，需要手动关闭

		else:
			Msg =  "文章url已经存在"
			wp_logging(Msg=Msg, allow_print=True)

		# now_filelinks_count = db_session.query(FileLink.id).count()
		# if now_filelinks_count - pre_filelinks_count > 0:
		# 	is_increased = True
		# else:
		# 	is_increased = False
		# Msg = '文章链接是否增加：%s ' % is_increased
		# wp_logging(Msg=Msg)
		# #todo 临时改成每次都全部抓取
		# is_increased = True
		# return is_increased

		#独立性的db_session要记得关闭
		db_session.close()

	def a_wait_to_pull_wiki(self):
		"""有关线程安全的测试，避免了 数据库创建出现 实例重复创建的错误。"""
		import threading
		lock = threading.Lock()

		l = [name for name in 'abcdefghijklmnopqrst!@#$%^&*()_+=-']
		l_all = []
		is_creading_list=list()
		for i in range(50000):
			l_all.append(l)


		from utility.common import create_scoped_session
		new_scoped_session = create_scoped_session(DB_ENGINE, DB_BASE)

		def create_tag_from_list(list):
			for name in list:
				need_to_create = False
				# print 'x..'
				# lock.acquire()
				if not(name in is_creading_list):
					is_creading_list.append(name)
					need_to_create = True
				# lock.release()
				if need_to_create:
				# tag_inst = get_or_create(new_scoped_session,Tag, is_global=True, name=name)[0]
					tag_inst = get_or_create(session=self.db_session(),model=Tag, is_global=False, name=name)[0]
				# tag_inst = Tag.get_unique(session=new_scoped_session,name=name)
				# new_scoped_session.add(tag_inst)
				# try:
				# 	new_scoped_session.commit()
				# 	print 'create：%s ' % name
				# # except exc.IntegrityError,e:
				# # 	print 'tag:%s exist; error_msg:%s' % (tag_inst.name,e)
				# # except exc.InvalidRequestError,e:
				# # 	print 'tag:%s exist; error_msg:%s' % (tag_inst.name,e)
				# except Exception, e:
				# 	print e

					# print type(tag_inst),name

		pool = ThreadPool(10)
		start_time = time.clock()
		try:
			pool.map(create_tag_from_list, l_all)
		except Exception,e:
			Msg = '开始新线程报错：%s' % e
			wp_logging(Msg=Msg,allow_print=True)

		end_time = time.clock()
		exc_time = end_time - start_time
		print len(l)
		print len(l_all)
		print 'exc_time: %s ' % exc_time

	def grab_articles(self):
		file_links_inst = self.query_not_crawled_article_url()

		grab_articles_pool = ThreadPool(GRAB_ARTICLES_POOL_SIZE)
		# try:
		new_articles_count =  file_links_inst.count()
		if new_articles_count > 0:
			Msg = '建立抓取文章的线程池...开始抓取'
			wp_logging(Msg=Msg)
			try:
				grab_articles_pool.map(self.grab_article, file_links_inst)
			except Exception,e:
				Msg = '开始新线程报错：%s' % e
				wp_logging(Msg=Msg,allow_print=True)

		else:
			Msg = '没有新文章更新...'
			wp_logging(Msg=Msg)

		# except Exception,e:
		# 	Msg = '[线程池](抓取文章)-->失败：%s' % e
		# 	wp_logging(Msg=Msg)
		# 	raise e

	def query_not_crawled_article_url(self):
		# 建立数据库链接
		db_session = self.db_session()
		file_links_inst = db_session.query(FileLink).filter_by(is_crawled=False)
		return file_links_inst

	def grab_article(self,url_inst):
		# 建立数据库链接
		db_session = self.db_session()
		r = None
		try:
			r = requests.get(url_inst.url, headers=self.headers)
		except Exception, e:
			Msg = '链接到文件URL时出现异常(下次再抓取）：%s' % e
			wp_logging(Msg=Msg)
			db_session.close()

			return
		if r.status_code is not 200:
			Msg = "首页抓取不是200,返回状态码：" + str(r.status_code)
			wp_logging(Msg=Msg)
			db_session.close()
			return

		h = pq(r.content)
		body = h('.entry')
		#匹配中文，记得要进行编码
		old_body_str =str(unicode(body).encode('utf-8'))

		#todo 抓取文章的发布时间


		#todo 排除没有包含所需要的网盘资源地址的文件。

		#抓取主体
		old_body = re.split('<span style="color: #ff0000;"><strong>Premium Dowload ゴッド会員 高速ダウンロード</strong></span><br />',old_body_str)
		# old_body = old_body[0][:-53]

		#抓取文章标题
		title = h('.title-single')
		title_unicode = unicode(title.html())
		title_str = unicode(title.html()).encode('utf-8')
		if len(title_str) < 0:
			Msg = "失败! 抓取文章标题!"
			wp_logging(Msg=Msg)
			db_session.close()
			return
		Msg = "抓取文章标题：" + str(unicode(title.html()).encode('utf-8'))
		wp_logging(Msg=Msg, allow_print=False)

		# 创建 文章实例
		# new_article = get_or_create(session=db_session, model=Article,title = title_unicode)[0]
		new_article = db_session.query(Article).filter_by(title=title_unicode).first()
		if new_article is None:
			new_article = Article(title=title_unicode)
		Msg =  "创建文章实例（--> 文章标题）" + title_unicode
		wp_logging(Msg=Msg, allow_print=False)

		#todo 抓取文章发布时间

		# 保存文章的来源地址
		file_link_inst = get_or_create(session=db_session, is_global=True, model=FileLink,url=url_inst.url,website=self.website)[0]
		new_article.file_link = file_link_inst

		#todo 抓取作者，拍摄电影的俱乐部
		#抓取电影分类
		categories = h('a[rel="category tag"]')
		# categories_text_list = []
		for category in categories:
			if category is not None:
				category_text = unicode(category.text)
				if not(category_text in CATEGORY_LIST_IN_DB_SESSION):
					CATEGORY_LIST_IN_DB_SESSION.append(category_text)
					category_instanc = get_or_create(session=db_session,is_global=True, model=Category,name=category_text)[0]
					if not(category_instanc in new_article.categories):
						new_article.categories.append(category_instanc)
				Msg = "抓取文章分类：" + category_text
				wp_logging(Msg=Msg, allow_print=False)

		#抓取tag,使用非贪婪模式
		tags_re_str = r'tag/.*?>(.*?)</a>'
		tags_re = re.compile(tags_re_str)
		tags = re.findall(tags_re, old_body_str)
		for tag in tags:
			Msg = "抓取文章标签：" + tag
			wp_logging(Msg=Msg, allow_print=False)
			if tag is not None:
				tag = unicode(tag)
				if not(tag in TAG_LIST_IN_DB_SESSION):
					TAG_LIST_IN_DB_SESSION.append(tag)
					tag_inst = get_or_create(session=db_session, is_global=True, model=Tag, name=tag)[0]
					if not(tag_inst in new_article.tags):
						new_article.tags.append(tag_inst)
						Msg = "添加文章标签：" + tag
						wp_logging(Msg=Msg, allow_print=False)

		#抓取old_download_links
		wp_logging(Msg="开始抓取old download links", allow_print=False)
		old_download_links_re_str = r'(http://www.uploadable.ch/file/.*?)["<]'
		old_download_links_re = re.compile(old_download_links_re_str)
		old_download_links = re.findall(old_download_links_re, old_body_str)
		#todo 临时测试：6个已经上传好的压缩文件
		# old_download_links = [
		# 	'http://www.uploadable.ch/file/4XBstq46gFbN/chrome.part1.rar',
		# 	'http://www.uploadable.ch/file/dGV4kpjY4XZ6/chrome.part2.rar',
		# 	'http://www.uploadable.ch/file/AF3ufw5qsQvp/chrome.part3.rar',
		# 	'http://www.uploadable.ch/file/FWMcqgNY6BZr/chrome.part4.rar',
		# 	'http://www.uploadable.ch/file/CtSRpcYSZkqG/chrome.part5.rar',
		# 	'http://www.uploadable.ch/file/Ud29HCTsFmWu/chrome.part6.rar',
		# ]
		#todo 初始化后台浏览器 准备下载
		# driver = FirefoxDriver()
		# driver.driver = driver.get_new_driver()

		for old_download_link in old_download_links:
			#抓取该链接的文件名和文件大小
			file_name = ''
			file_size = ''
			content = self.get_filename_by_url(old_download_link)
			if content.get('status'):
				dict_params = {}
				dict_params.update(dict(
					status='waiting_download',
					file_name=file_name[1:-1],#不要包括括号
					file_size=file_size,
					url=old_download_link,
					website=self.website
					))
				old_download_link_inst = get_or_create(session=db_session, is_global=True, model=OldDownloadLink,filter_cond={'url':old_download_link},**dict_params)[0]
				new_article.old_download_links.append(old_download_link_inst)
				Msg = "抓取 old download link: %s" % old_download_link
				wp_logging(Msg=Msg, allow_print=False)
			else:
				db_session.close()
				return


			#todo 测试下载，暂时放在这里,不用使用多线程
			# driver.download_file(old_download_link_inst)
			# download_pool = self.get_download_pool(processes=10)
			# download_pool.map(driver.download_file,new_article.old_download_links)


		#取文件名（已经被其他代码替代）
		# file_name=''
		# file_name_re_strs  = [r'>(.*?).part\d.rar',r'/?([\d\w]*[-]*[\w\d]*)\.wmv']
		# for file_name_re_str in file_name_re_strs:
		# 	file_name_re = re.compile(file_name_re_str)
		# 	file_names = re.findall(file_name_re, old_body_str)
		# 	if len(file_names) == 0:
		# 		continue
		# 	for file_name_ in file_names:
		# 		file_name = file_name_
		# 		Msg =  "抓取文件名： "+ file_name
		# 		wp_logging(Msg=Msg)
		# 		break
		# 创建 文章实例
		# if len(file_name):
		# 	self.article_files.update(
		# 		file_name = file_name,
		# 		website = self.website,
		# 	)
		# 	new_article = Article(**self.article_files)
		# 	Msg =  "创建文章实例： "+ new_article.title
		# 	wp_logging(Msg=Msg)
		#todo 临时查看文章的所有属性
		# attr_list = dir(new_article)
		# for attr in attr_list:
		# 	# ss= 'ss'
		# 	if not attr.startswith('__'):
		# 		v = getattr(new_article,attr,'empty')
		# 		Msg =  "文章-->属性：%s  |  值：%s " % (attr, v)
		# 		wp_logging(Msg=Msg)

		#todo 实际操作时，要提交保存到数据库。

		#将url状态改成 已经被抓取
		# db_session_1 = self.db_session()
		# url_inst_ = db_session_1.query(FileLink).filter_by(id=url_inst.id).first()
		url_inst_ = get_or_create(session=db_session,is_global=True, model=FileLink,id=url_inst.id)[0]
		url_inst_.is_crawled = True
		# db_session_1.add(url_inst_)
		# db_session_1.commit()
		#提交文章

		db_session.add(new_article)
		db_session.add(url_inst_)
		db_session.commit()
		db_session.close()
		Msg='article successful'
		wp_logging(Msg=Msg)

	def get_filename_by_url(self,url):

		content = dict(
			status = True,
			file_name ='',
			file_size = ''
		)
		r = None
		try:
			r = requests.get(url=url, headers=self.uploadable_headers)
		except Exception,e:
			Msg = "链接到URL失败（%s）：%s" % (url,e)
			wp_logging(Msg=Msg)
			content.update(status=False)
			return content

		if r.status_code is not 200:
			Msg = "开始抓取指定下载链接的文件名，及大小：%s \r\n \
				  抓取失败！状态码:%s " % (url, str(r.status_code))
			wp_logging(Msg=Msg)
			content.update(status=False)
			return content

		h = pq(r.content)
		file_name = h('#file_name').attr('title')
		file_size_and_unit = h('.filename_normal').html()
		file_size = file_size_and_unit[1:-4]
		file_size_unit = file_size_and_unit[-3:-1]
		Msg = "抓取文件名：%s，文件夹大小：%s " % (file_name, file_size)
		wp_logging(Msg=Msg, allow_print=False)
		content.update(file_name=file_name,file_size=file_size,file_size_unit=file_size_unit)
		#匹配中文，记得要进行编码
		# old_body_str =str(unicode(body).encode('utf-8'))
		return content

	def get_download_pool(self, processes=10):
		'''记得退出pool'''
		pool = ThreadPool(processes)
		#
		# pool.close()
		# pool.join()
		return pool

	def temp_make_s_links(self):
		#把文章ID=1的 旧下载链接换成 测试的6个下载链接
		db_sesion = self.db_session()
		article = db_sesion.query(Article).filter_by(id=1).first()
		odls = article.old_download_links
		print len(odls)
		#删除旧链接
		for odl in odls:
			db_sesion.delete(odl)
		db_sesion.commit()

		from settings import s_links
		#change to test links
		file_size = '1.00'
		file_size_unit='MB'
		for s_link in s_links:
			file_name = s_link.split('/')[-1]
			if file_name == 'chrome.part6.rar':
				file_size = '255.10'
				file_size_unit='KB'
			# link_inst = OldDownloadLink(url=s_link,file_name=file_name,file_size=1.00)
			filter_cond = dict(url=s_link)
			kwargs_dict = dict(url=s_link, file_name=file_name, file_size=file_size,file_size_unit=file_size_unit)
			link_inst = get_or_create(session=db_sesion,is_global=True, model=OldDownloadLink, filter_cond=filter_cond,**kwargs_dict)[0]
			article.old_download_links.append(link_inst)
		db_sesion.add(article)
		db_sesion.commit()
		for odl_inst in article.old_download_links:
			print 'old:%s' % odl_inst.url


		db_sesion.close()

	def file_download_system(self):
		while True:
			self.check_pre_downloading_file()
			#todo 如果打开下载链接后，“Download Now”没有出现，需要重新登录或者重新载入
			#正在下载的文件小于设定数（5），并且等待下载的列表为空
			if len(WAITING_DOWNLOAD_LIST) <= 0:
				#查询最新文章的status = waiting_download 的URL并加入待下载列表
				self.get_wait_to_download_urls()

			if len(DOWNLOADING_LIST) < MAX_DOWNLOADING_NUMBER and len(WAITING_DOWNLOAD_LIST) > 0:
				url_inst = WAITING_DOWNLOAD_LIST.pop()
				DOWNLOADING_LIST.append(url_inst)
				url_inst.status = 'downloading'
				#todo try...
				self.update_inst(url_inst)
				self.download_file(url_inst)

			time.sleep(5)

	def update_inst(self,inst):
		db_session = self.db_session()
		db_session.add(inst)
		db_session.commit()
		db_session.close()

	def download_file(self,url_inst):

		# if self.driver.login_time is None:
		# 	self.get_firefox_driver()
		#登录超时检测
		# self.check_login_expire()
		#todo 直接做成 连接“下载链接”，判断 “立即下载” 按钮是否出现。没有就重新登录。
		been_download =  self.driver.download_file(url_inst)
		#todo 跟踪文件是否成功下载，文件存在，并且大小正确
		check_downloaded = threading.Thread(target=self.check_file_is_downloaded, args=(url_inst,))
		check_downloaded.start()
		Msg = '启动新线程：check_file_is_downloaded'
		wp_logging(Msg=Msg)


	def check_file_is_downloaded(self,url_inst):
		'''跟踪文件是否成功下载，文件存在，并且大小正确'''
		db_session = self.db_session()
		# file_path = DOWNLOAD_DIR + "/" + url_inst.file_name
		# file_real_size = float(url_inst.file_size) * FILE_UNIT_CONVERSION.get(url_inst.file_size_unit)
		file_path, file_real_size = self.get_file_path_and_real_size(url_inst)

		# 每5秒检查一次，超时，则文件状态改成waiting_download.
		# loop_count > 120 表示超时10分钟,实际环境用
		# loop_count > 6 表示超时30秒,测试用
		total_time = 0

		while True:
			if os.path.exists(file_path):
				downloaded_file_size = common_utility.get_file_size(file_path=file_path)
				Msg = 'file_name: %s \r\n' % url_inst.file_name.encode('utf8')
				Msg += 'downloaded_file_size:%s , file_real_size:%s ' % (downloaded_file_size,file_real_size )
				wp_logging(Msg=Msg)
				if downloaded_file_size == file_real_size:
					url_inst.status = 'downloaded'
					db_session.add(url_inst)
					db_session.commit()
					Msg = 'have download ：%s' % url_inst.file_name.encode('utf8')
					wp_logging(Msg=Msg)
					DOWNLOADING_LIST.remove(url_inst)
					db_session.close()
					#移动文件到对应文章的已下载文件夹
					dir = ARTICLE_FILES_DIR +'/'+str(url_inst.article_id)+'/'+'downloaded_files'
					common_utility.move_file_to_dir(file_path,dir)
				break
			if total_time > 600: #超过十分钟
				url_inst.status = 'waiting_download'
				# self.update_inst(url_inst)
				db_session.add(url_inst)
				db_session.commit()
				Msg = '下载超时！： ：%s ，file changed to waiting_download.' % url_inst.file_name.encode('utf8')
				wp_logging(Msg=Msg)
				Msg = '目前正在下载列表的状态：%s \r\n' % DOWNLOADING_LIST
				DOWNLOADING_LIST.remove(url_inst)
				Msg += '移除 %s ，正在下载列表状态：%s \r\n' % (url_inst.file_name.encode('utf8'), DOWNLOADING_LIST)
				Msg += '第 %s 次检查下载文件：%s ' % (loop_count, url_inst.file_name.encode('utf8'))
				wp_logging(Msg=Msg)
				db_session.close()
				break
			time.sleep(5)
			total_time += 5

			#todo 根据文件大小，下载速度，得到时间+5分钟，超时，则改url状态为等待下载，下次再下载


	def check_login_expire(self):
		#登录时间超过30分钟
		logon_time = datetime.now() - self.driver.login_time
		logon_time_minutes = (logon_time.seconds//60)%60
		#todo 根据文章的发布时间，下载最新发布的3部电影。
		if logon_time_minutes >30:
			self.get_firefox_driver()

	def get_firefox_driver(self):
		#todo 记得重新处理异常
		try:
			self.driver.driver = self.driver.get_new_driver()
			self.driver.login_time = datetime.now()
		except Exception,e:
			raise e
			# try:
			# 	self.driver.driver.close()
			# except Exception,e:
			# 	raise e
			# self.get_firefox_driver()
	def get_file_path_and_real_size(self,url_inst):
		file_path = DOWNLOAD_DIR + "/" + url_inst.file_name
		file_real_size = url_inst.file_size + url_inst.file_size_unit[0]
		return (file_path, file_real_size)

	def check_pre_downloading_file(self):
		db_session = self.db_session()

		# 先判断那些 downloading 状态的文件（不在downloading_list里） 是否已经下载好。
		odl_insts = db_session.query(OldDownloadLink).filter(OldDownloadLink.status=='downloading').all()

		for odl_inst in odl_insts:
			file_path, file_real_size = self.get_file_path_and_real_size(odl_inst)
			# file_path = DOWNLOAD_DIR + "/" + odl_inst.file_name
			# file_real_size = float(odl_inst.file_size) * FILE_UNIT_CONVERSION.get(odl_inst.file_size_unit)
			#temp
			#~end temp
			if any(odl_inst.file_name == url_inst.file_name for url_inst in DOWNLOADING_LIST):
				#不再当前下载list里面
				Msg = '%s 正在下载...不需要在这里检查是否下载成功。' % odl_inst.file_name.encode('utf8')
				wp_logging(Msg=Msg)
				continue
			if os.path.exists(file_path):
				downloaded_file_size = common_utility.get_file_size(file_path=file_path)
				if downloaded_file_size == file_real_size:
					odl_inst.status = 'downloaded'
					db_session.add(odl_inst)
					db_session.commit()
					Msg = '没有在downloading_list里的文件：%s，但已经下载好了，改成状态：downloaded。' % odl_inst.file_name.encode('utf8')
					wp_logging(Msg=Msg)
					#移动文件到对应文章的已下载文件夹
					dir = ARTICLE_FILES_DIR +'/'+str(odl_inst.article_id)+'/'+'downloaded_files'
					common_utility.move_file_to_dir(file_path,dir)
				else:
					os.remove(file_path)
					odl_inst.status = 'waiting_download'
					db_session.add(odl_inst)
					db_session.commit()
					Msg = '文件状态为downloading却没有下载完整的文件：%s，已经改成waiting_download状态。' % odl_inst.file_name.encode('utf8')
					wp_logging(Msg=Msg)
			else:
				odl_inst.status = 'waiting_download'
				db_session.add(odl_inst)
				db_session.commit()
				Msg = '文件状态为downloading却没有下载完整的文件：%s，已经改成waiting_download状态。' % odl_inst.file_name.encode('utf8')
				wp_logging(Msg=Msg)
	def get_wait_to_download_urls(self):

		#实际情况，过滤条件改成含有未下载地址的，最新发布的一篇文章
		db_session = self.db_session()
		article = db_session.query(Article).filter_by(id=1).first()
		for url_inst in article.old_download_links:
			if url_inst.status == 'waiting_download':
				if url_inst not in DOWNLOADING_LIST:
					WAITING_DOWNLOAD_LIST.append(url_inst)
		db_session.close()
		# for inst in WAITING_DOWNLOAD_LIST:
		# 	self.test_print_inst(inst)
		# return db_session
	def test_print_inst(self,inst):
		print inst.url

	def file_unrar_system(self):
		while True:
			#todo 如果打开下载链接后，“Download Now”没有出现，需要重新登录或者重新载入
			#正在下载的文件小于设定数（5），并且等待下载的列表为空
			if len(UNRARING_LIST) + len(RARING_LIST) < MAX_RAR_AND_UNRAR_NUMBER:
				#查询最新文章的status = waiting_download 的URL并加入待下载列表
				if len(WAITING_UNRAR_LIST) <= 0:
					self.get_wait_to_unrar_urls()

			if len(UNRARING_LIST) + len(RARING_LIST) < MAX_RAR_AND_UNRAR_NUMBER and len(WAITING_UNRAR_LIST) > 0:
				article_inst = WAITING_UNRAR_LIST.pop()
				UNRARING_LIST.append(article_inst)
				# url_inst.status = 'downloading'
				#todo try...
				# self.update_inst(url_inst)
				self.unrar_file(article_inst)

			time.sleep(5)


	def get_wait_to_unrar_urls(self):

		db_session = self.db_session()
		articles = db_session.query(Article).join(Article.old_download_links).filter(OldDownloadLink.status=='downloaded').all()
		if len(articles) < 0:
			return

		for article in articles:
			all_be_downloaded = True
			for odl in article.old_download_links:
				if odl.status != 'downloaded':
					all_be_downloaded = False
			if all_be_downloaded:
				WAITING_UNRAR_LIST.append(article)

		# print article.id
		db_session.close()

	def unrar_file(self, article_inst):
		check_unrared = threading.Thread(target=self.check_file_is_unrared, args=(article_inst,))
		check_unrared.start()
		Msg = '启动新线程：check_unrared'
		wp_logging(Msg=Msg)

	def check_file_is_unrared(self,article_inst):
		db_session = self.db_session()
		db_session.add(article_inst)
		url_inst = article_inst.old_download_links[0]

		file_path = ARTICLE_FILES_DIR +'/'+ str(article_inst.id) +'/'+'downloaded_files/'+ url_inst.file_name
		print file_path
		dir = ARTICLE_FILES_DIR +'/'+ str(article_inst.id) +'/'+'unrared_files/'
		if not os.path.exists(file_path):
			Msg =  '%s 文件不存在，无法解压！' % url_inst.file_name.encode('utf8')
			wp_logging(Msg=Msg)
			return
		if not os.path.exists(dir):
			os.makedirs(dir)

		cmd = '/usr/bin/unrar x ' + file_path +' ' + dir

		command = ShellCommand(cmd)
		result_dic = command.run(timeout=10)
		#状态改成正在解压中
		q = db_session.query(OldDownloadLink).filter(OldDownloadLink.article_id==article_inst.id)
		q.update({'status': 'unraring'})
		db_session.commit()
		if result_dic.get('status') == 0:
			Msg = '%s 解压成功!' % url_inst.file_name.encode('utf8')
			wp_logging(Msg=Msg)
			q.update({'status': 'unrared'})
			db_session.commit()
		elif result_dic.get('status') == 'Time Out':
			Msg = '%s 解压超时!' % url_inst.file_name.encode('utf8')
			wp_logging(Msg=Msg)
			#改成downloaded状态
			q.update({'status': 'downloaded'})
			db_session.commit()
		else:
			raise Exception,'解压发生为止错误：%s ' % result_dic.get('status')
		UNRARING_LIST.remove(article_inst)
		db_session.close()
	def file_rar_system(self):
		while True:
			#todo 如果打开下载链接后，“Download Now”没有出现，需要重新登录或者重新载入
			#正在下载的文件小于设定数（5），并且等待下载的列表为空
			if len(UNRARING_LIST) + len(RARING_LIST) < MAX_RAR_AND_UNRAR_NUMBER:
				#查询最新文章的status = waiting_download 的URL并加入待下载列表
				if len(WAITING_RAR_LIST) <= 0:
					self.get_wait_to_rar_urls()

			if len(UNRARING_LIST) + len(RARING_LIST) < MAX_RAR_AND_UNRAR_NUMBER and len(WAITING_RAR_LIST) > 0:
				article_inst = WAITING_RAR_LIST.pop()
				RARING_LIST.append(article_inst)
				# url_inst.status = 'downloading'
				#todo try...
				# self.update_inst(url_inst)
				self.rar_file(article_inst)

			time.sleep(5)
	def get_wait_to_rar_urls(self):
		db_session = self.db_session()
		articles = db_session.query(Article).join(Article.old_download_links).filter(OldDownloadLink.status=='unrared').all()
		if len(articles) < 0:
			return

		for article in articles:
			all_be_unrared = True
			for odl in article.old_download_links:
				if odl.status != 'unrared':
					all_be_unrared = False
			if all_be_unrared:
				WAITING_RAR_LIST.append(article)

		# print article.id
		db_session.close()
	def rar_file(self, article_inst):
		check_rared = threading.Thread(target=self.check_file_is_rared, args=(article_inst,))
		check_rared.start()
		Msg = '启动新线程：check_rared'
		wp_logging(Msg=Msg)

	def check_file_is_rared(self,article_inst):
		db_session = self.db_session()
		db_session.add(article_inst)
		url_inst = article_inst.old_download_links[0]

		# file_path = ARTICLE_FILES_DIR +'/'+ str(article_inst.id) +'/'+'unrared_files/'+ url_inst.file_name
		unrared_dir = ARTICLE_FILES_DIR +'/'+ str(article_inst.id) +'/'+'unrared_files/'
		rared_dir = ARTICLE_FILES_DIR +'/'+ str(article_inst.id) +'/'+'rared_files/'

		file_names = common_utility.get_files_in_dir(unrared_dir)
		# if not os.path.exists(file_path):
		# 	Msg =  '%s 文件不存在，无法解压！' % url_inst.file_name.encode('utf8')
		# 	wp_logging(Msg=Msg)
		# 	return
		if not os.path.exists(rared_dir):
			os.makedirs(rared_dir)
		#-v10m 分卷大小1m , -ep 表示：不要把文件的路径层也照样复制进去
		cmd = '/usr/bin/rar a -m0 -v10m -ep ' + rared_dir +'/' +str(url_inst.file_name.split('.')[0])
		#指定压缩哪些文件
		if file_names <=0:
			RARING_LIST.remove(article_inst)
			return
		for name in file_names:
			print 'name%s' % name
			cmd += ' ' + unrared_dir+'/'+str(name)

		print cmd

		command = ShellCommand(cmd)
		result_dic = command.run(timeout=10)
		#状态改成正在压缩中
		q = db_session.query(OldDownloadLink).filter(OldDownloadLink.article_id==article_inst.id)
		q.update({'status': 'raring'})
		db_session.commit()
		if result_dic.get('status') == 0:
			Msg = '%s 压缩成功!' % url_inst.file_name.encode('utf8')
			wp_logging(Msg=Msg)
			q.update({'status': 'rared'})
			db_session.commit()
		elif result_dic.get('status') == 'Time Out':
			Msg = '%s 压缩超时!' % url_inst.file_name.encode('utf8')
			wp_logging(Msg=Msg)
			#改成unrared状态
			q.update({'status': 'unrared'})
			db_session.commit()
		else:
			raise Exception,'压缩发生为止错误：%s ' % result_dic.get('status')
		RARING_LIST.remove(article_inst)
		db_session.close()

	def file_upload_system(self):
		while True:
			#todo 如果打开下载链接后，“Download Now”没有出现，需要重新登录或者重新载入
			#正在下载的文件小于设定数（5），并且等待下载的列表为空
			if len(UPLOADING_LIST)  < MAX_UPLOAD_NUMBER:
				#查询最新文章的status = waiting_download 的URL并加入待下载列表
				if len(WAITING_UPLOAD_LIST) <= 0:
					self.get_wait_to_upload_urls()

			if len(UPLOADING_LIST) < MAX_UPLOAD_NUMBER and len(WAITING_UPLOAD_LIST) > 0:
				ndl_inst = WAITING_UPLOAD_LIST.pop()
				UPLOADING_LIST.append(ndl_inst)
				# url_inst.status = 'downloading'
				#todo try...
				# self.update_inst(url_inst)
				self.upload_file(ndl_inst)

			time.sleep(5)

	def get_wait_to_upload_urls(self):
		db_session = self.db_session()
		articles = db_session.query(Article).join(Article.old_download_links).filter(OldDownloadLink.status=='rared').all()
		if len(articles) < 0:
			return

		for article in articles:
			all_be_rared = True
			for odl in article.old_download_links:
				if odl.status != 'rared':
					all_be_rared = False
			if all_be_rared:
				ndl_insts = article.new_download_links
				if len(ndl_insts)==0:
					rared_dir = ARTICLE_FILES_DIR +'/'+ str(article.id) +'/'+'rared_files/'
					files_name = common_utility.get_rared_files_name(rared_dir)
					for file_name in files_name:
						#url 暂时用文件名替代。以后判断如果http没有在URL里，就需要更新URL
						ndl_inst = NewDownloadLink(url=file_name,file_name=file_name, status='waiting_uploaded')
						article.new_download_links.append(ndl_inst)
						WAITING_UPLOAD_LIST.append(ndl_inst)
					db_session.add(article)
					db_session.commit()

				for ndl_inst in ndl_insts:
					if ndl_inst.status == 'waiting_uploaded':
						WAITING_UPLOAD_LIST.append(ndl_inst)

		db_session.close()

	def upload_file(self, ndl_inst):
		check_uploaded = threading.Thread(target=self.check_file_is_uploaded, args=(ndl_inst,))
		check_uploaded.start()
		Msg = '启动新线程：check_uploaded'
		wp_logging(Msg=Msg)

	def check_file_is_uploaded(self, ndl_inst):
		db_session = self.db_session()
		db_session.add(ndl_inst)
		# url_inst = article_inst.old_download_links[0]

		file_name = ndl_inst.file_name.encode('utf8')
		rared_dir = ARTICLE_FILES_DIR +'/'+ str(ndl_inst.article_id) +'/'+'rared_files/'
		uploaded_dir = ARTICLE_FILES_DIR +'/'+ str(ndl_inst.article_id) +'/'+'uploaded_files/'

		file_with_abspath = rared_dir + file_name

		# files_with_abspath = common_utility.get_files_with_pull_path(rared_dir)

		if not os.path.exists(file_with_abspath):
			Msg='%s 还没上传就已经被删除了！' % file_name
			wp_logging(Msg=Msg)
			UPLOADING_LIST.remove(ndl_inst)
			db_session.close()
			return

		if not os.path.exists(uploaded_dir):
			os.makedirs(uploaded_dir)

		# if files_with_abspath <=0:
		# 	UPLOADING_LIST.remove(article_inst)
		# 	return
		# db_session.close()
		#
		# rared_file_count = len(files_with_abspath)
		# for file in files_with_abspath:
		# 	#判断该文件是否已经上传（获取还没有新url信息，但已经上传到服务器，并关联到文章了）
		# 	db_session = self.db_session()
		# 	file_name = os.path.basename(file)
		# 	q = db_session.query(NewDownloadLink).filter_by(file_name=file_name).all()
		# 	if len(q)>0:
		# 		continue
		# 	db_session.close()
		#
		# 	upload_single_file = threading.Thread(target=self.upload_file_thread, args=(article_inst, file, rared_file_count))
		# 	upload_single_file.start()
		# 	Msg = '启动新线程：upload_single_file'
		# 	wp_logging(Msg=Msg)
	#
	# def upload_file_thread(self,article_inst,file,rared_file_count):
	# 	db_session = self.db_session()
	# 	db_session.add(article_inst)
	# 	url_inst = article_inst.old_download_links[0]

		fileav_ftp = FilmAvFtp()
		fileav_ftp.login()
		# file_name_not_ext = os.path.basename(file)
		with open(file_with_abspath,'rb') as file_to_uploaed:
			try:
				fileav_ftp.ftp.storbinary('STOR ' + file_name,
						   file_to_uploaed,
						   fileav_ftp.blocksize,
						   )

			except Exception as e:
				ndl_inst.status = 'waiting_uploaded'
				db_session.add(ndl_inst)
				db_session.commit()
				db_session.close()
				UPLOADING_LIST.remove(ndl_inst)
				Msg = '%s ->upload fail！error:%s' % (file_name, e)
				wp_logging(Msg=Msg)
				db_session.close()
				return
		#没有异常，则文件上传成功
		GRAB_NEW_UR = True # 告诉系统，需要抓取新链接了。
		ndl_inst.status = 'uploaded'
		db_session.add(ndl_inst)
		db_session.commit()
		db_session.close()
		Msg = '%s ->upload OK！' % file_name
		wp_logging(Msg=Msg)
		UPLOADING_LIST.remove(ndl_inst)
		db_session.close()
		# #检查是否都上传好了，如果 len（ewDownloadLink）==rared_file_count,表示全部都上传好了
		# new_download_link = db_session.query(NewDownloadLink).filter(NewDownloadLink.article_id==article_inst.id).all()
		# if new_download_link == rared_file_count:
		# 	#状态改成正在压缩中
		# 	q = db_session.query(OldDownloadLink).filter(OldDownloadLink.article_id==article_inst.id)
		# 	q.update({'status': 'uploaded'})
		# 	db_session.commit()
		# 	Msg = '%s 全部已经上传成功!' % file_name.encode('utf8')
		# 	wp_logging(Msg=Msg)





if __name__ == '__main__':

	filmav_grab = Filmav_Grab()
	# filmav_grab.a_wait_to_pull_wiki()
	test = False
	# 本次程序总轮循次数统计
	for_count = 1
	#test
	# filmav_grab.get_wait_to_unrar_urls()
	while True:
		Msg = "=====第 %s 次总轮循" %  for_count
		wp_logging(Msg=Msg)

		print 'DOWNLOADING_LIST : %s ' % DOWNLOADING_LIST
		#temp 创建测试数据等。

		if test:
			filmav_grab.temp_make_s_links() # 创建6个测试下载链接 记得最后一个文件大小改成255.10 KB
		#todo test

		# #文件下载，解压，压缩，上传 轮循
		# if not filmav_grab.DOWNLOAD_SYSTEM_IS_RUNNING:
		# 	download_thread = threading.Thread(target=filmav_grab.file_download_system)
		# 	download_thread.start()
		# 	filmav_grab.DOWNLOAD_SYSTEM_IS_RUNNING = True
		# 	print 'start download system... '
		#
		# #todo 文件解压，正在解压/正在压缩列表小于1时，处理新的解压任务
		# if not filmav_grab.UNRAR_SYSTEM_IS_RUNNING:
		# 	print 'start rar system... '
		# 	print 'RARING_LIST %s ' % RARING_LIST
		# 	rar_thread = threading.Thread(target=filmav_grab.file_rar_system)
		# 	rar_thread.start()
		# 	filmav_grab.RAR_SYSTEM_IS_RUNNING = True



		# #todo 文件压缩，正在解压/正在压缩列表小于1时，不处理新的解压任务
		# if not filmav_grab.RAR_SYSTEM_IS_RUNNING:
		# 	print 'start rar system... '
		# 	print 'RARING_LIST %s ' % RARING_LIST
		# 	rar_thread = threading.Thread(target=filmav_grab.file_rar_system)
		# 	rar_thread.start()
		# 	filmav_grab.RAR_SYSTEM_IS_RUNNING = True
		# 	print 'start rar system... '

		#todo 文件上传，待正在上传列表小于10时，添加新的待上传文件地址
		# if not filmav_grab.UPLOAD_SYSTEM_IS_RUNNING:
		#
		# 	print 'UPLOADING_LIST %s ' % UPLOADING_LIST
		# 	upload_thread = threading.Thread(target=filmav_grab.file_upload_system)
		# 	upload_thread.start()
		# 	filmav_grab.UPLOAD_SYSTEM_IS_RUNNING = True
		# 	print 'start upload system... '


		#todo 抓取上传的地址
		if GRAB_NEW_URL_FIRST or GRAB_NEW_URL:
			if GRAB_NEW_URL:
				#刚刚上传，需要等网盘站生成下载地址
				time.sleep(10)

		print 'man process sleep 5... '
		# #todo 为每一个大步 建立try机制？中止或重启，并发邮件通知操作者

		#自动抓取网站指定页面范围的所有文章URL(也是自动更新功能），
		# filmav_grab.grab_article_url(page_end=1)
		#自动抓取未抓取的文章详细内容
		# filmav_grab.grab_articles()
		test = False
		for_count += 1
		time.sleep(5)

	# filmav_grab.get(url='http://filmav.com/53049.html')
	# filmav_grab.get_image(url='http://filmav.com/52792.html')
	# article_urls = filmav_grab.grab_article_url()
	# filmav_grab.save_article_url(article_urls)
	# filmav_grab.grab_article_body()