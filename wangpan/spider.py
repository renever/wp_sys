# -*- coding: utf-8 -*-
import re
import requests
import time
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
from models import FileLink, Article,Image,OldDownloadLink,NewDownloadLink,Tag, Category

from utility import create_session, wp_logging, get_or_create, FirefoxDriver
from multiprocessing.dummy import Pool as ThreadPool
import unicodedata
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# logging.config.fileConfig("/home/l/app/learning/wangpan/logging.conf")
# logger = logging.getLogger("wp")

class Filmav_Grab():

	def __init__(self):
		db_session = self.db_session()
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
		self.driver = FirefoxDriver()

		self.global_db_session = db_session



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





	def grab_article_url(self,page_start=1,page_end=1):
		"""
		抓取首页每篇文章链接


		"""
		#todo 抓取制定页面范围的所有文件的链接。
		#todo 循环各个页面，具体抓取文章内容时，记得根据文章链接最后数字进行排序，另，判断是否有有效的下载地址。
		BASE_URL = 'http://filmav.com/page/'
		article_urls=[]
		for page_number in range(page_start,page_end+1):
			url = BASE_URL + str(page_number)
			r = requests.get(url=url, headers=self.headers)

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
			is_increased = self.save_article_url(article_urls)

			if is_increased:
				continue
			else:
				break

		return article_urls, is_increased

	def save_article_url(self, article_urls):
		db_session = self.db_session()
		is_increased = None
		pre_filelinks_count = db_session.query(FileLink.id).count()
		for url in article_urls:
			url_instance,is_existed = get_or_create(session=db_session, is_global=True, model=FileLink,url=url,website=self.website)
			if is_existed:
				Msg =  "文章url已经存在"
				wp_logging(Msg=Msg, allow_print=False)
			else:
				try:
					db_session.add(url_instance)
					db_session.commit()
					Msg =  "已保存文章url： " + url
					wp_logging(Msg=Msg, allow_print=False)
				except exc.IntegrityError, e :
					Msg =  "保存文章url失败： " + e.message
					wp_logging(Msg=Msg, allow_print=False)
					#如果db_session.commit() 出现异常，需要手动关闭
					db_session.close()

		now_filelinks_count = db_session.query(FileLink.id).count()
		if now_filelinks_count - pre_filelinks_count > 0:
			is_increased = True
		else:
			is_increased = False
		Msg = '文章链接是否增加：%s ' % is_increased
		wp_logging(Msg=Msg)
		return is_increased

	def test(self):
		file_links_inst_list = self.query_not_crawled_article_url()
		file_links_inst = file_links_inst_list[0]
		print type(file_links_inst)
		print file_links_inst.id
		file_links_inst.is_crawled = True

		self.global_db_session.add(file_links_inst)
		self.global_db_session.commit()

	def grab_articles(self):
		file_links_inst = self.query_not_crawled_article_url()

		grab_articles_pool = ThreadPool(5)
		# try:
		Msg = '建立抓取文章的线程池...开始抓取'
		wp_logging(Msg=Msg)
		grab_articles_pool.map(self.grab_article, file_links_inst)
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
		r = requests.get(url_inst.url, headers=self.headers)

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
		# old_body = old_body[0][:-53]

		#抓取文章标题
		title = h('.title-single')
		title_unicode = unicode(title.html())
		title_str = unicode(title.html()).encode('utf-8')
		if len(title_str) < 0:
			Msg = "失败! 抓取文章标题!"
			wp_logging(Msg=Msg)
			return
		Msg = "抓取文章标题：" + str(unicode(title.html()).encode('utf-8'))
		wp_logging(Msg=Msg)

		# 创建 文章实例
		# new_article = get_or_create(session=db_session, model=Article,title = title_unicode)[0]
		new_article = db_session.query(Article).filter_by(title=title_unicode).first()
		if new_article is None:
			new_article = Article(title=title_unicode)
		Msg =  "创建文章实例（--> 文章标题）" + title_unicode
		wp_logging(Msg=Msg, allow_print=False)

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
				tag_unicode = unicode(tag)
				tag = tag_unicode
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
			file_name,file_size = self.get_filename_by_url(old_download_link)
			dict_params = {}
			dict_params.update(dict(
				status='waiting_download',
				file_name=file_name,
				file_size=file_size,
				url=old_download_link,
				website=self.website
				))
			old_download_link_inst = get_or_create(session=db_session, is_global=True, model=OldDownloadLink,filter_cond={'url':old_download_link},**dict_params)[0]
			new_article.old_download_links.append(old_download_link_inst)
			Msg = "抓取 old download link: %s" % old_download_link
			wp_logging(Msg=Msg, allow_print=False)

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
		db_session.add(url_inst_)
		db_session.add(new_article)
		db_session.commit()


	def get_filename_by_url(self,url):

		r = requests.get(url=url, headers=self.uploadable_headers)

		if r.status_code is not 200:
			Msg = "开始抓取指定下载链接的文件名，及大小：%s \r\n \
				  抓取失败！状态码:%s " % (url, str(r.status_code))
			wp_logging(Msg=Msg)
			return

		h = pq(r.content)
		file_name = h('#file_name').attr('title')
		file_size = h('.filename_normal').html()
		Msg = "抓取文件名：%s，文件夹大小：%s " % (file_name,file_size)
		wp_logging(Msg=Msg, allow_print=False)
		return file_name,file_size

		#匹配中文，记得要进行编码
		# old_body_str =str(unicode(body).encode('utf-8'))

	def get_download_pool(self, processes=10):
		'''记得退出pool'''
		pool = ThreadPool(processes)
		return pool
		#
		# pool.close()
		# pool.join()



	# def grap_atrical_details(self):

if __name__ == '__main__':

	filmav_grab = Filmav_Grab()
	# filmav_grab.test()

	#本次程序总轮循次数统计
	for_count = 1
	while True:
		Msg = "=====第 %s 次总轮循" %  for_count
		wp_logging(Msg=Msg)

		#todo 为每一个大步 建立try机制？中止或重启，并发邮件通知操作者
		#自动抓取网站指定页面范围的所有文章URL(也是自动更新功能），
		filmav_grab.grab_article_url(page_end=2)
		#自动抓取未抓取的文章详细内容
		filmav_grab.grab_articles()

		for_count += 1

		time.sleep(3)





	# filmav_grab.get(url='http://filmav.com/53049.html')
	# filmav_grab.get_image(url='http://filmav.com/52792.html')
	# article_urls = filmav_grab.grab_article_url()
	# filmav_grab.save_article_url(article_urls)
	# filmav_grab.grab_article_body()



