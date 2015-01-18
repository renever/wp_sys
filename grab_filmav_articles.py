
# -*- coding: utf-8 -*-
#第三方包
import requests
from pyquery import PyQuery as pq
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
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
#from utils import FirefoxDriver
from utils import create_session, wp_logging, get_or_create,  common_utility, GrabNewODL,\
				GrabNewODL_UPNET,GrabNewODL_SH
from utility.common import ShellCommand, FilmAvFtp
import codecs
import unicodedata
#系统包
import logging
import logging.config
from contextlib import closing
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime,date
import re
import time
import os
import json
import shutil
import threading
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
import sys
reload(sys)
sys.setdefaultencoding('utf8')
not_file_name_list = []
wait_to_uploaded_url = []
class Filmav_Grab():

	def __init__(self):
		self.headers = {
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
		self.blog_url = u'http://jpnewfilm.com'
		#todo 暂时屏蔽 driver 的初始化
		# self.driver = FirefoxDriver()




	def get(self,url):
		try:
			self.r = self.requests.get(url,headers = self.headers)
			logging.debug('获取网页成功')

		except Exception ,e:
			Msg = u'获取网页失败，原因：%s' % e
			logging.debug(Msg)

		return self.r

	def get_image(self,url):
		r = self.get(url=url)
		if r.status_code is not 200:
			Msg ='获取网页失败，无法进一步抓取图片'
			wp_logging(Msg=Msg)
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
			small_path--> 图片存于small_path,
			big_path-->图片存于big_path
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
					Msg = u'抓取图片成功，开始下载...'
					# print Msg
					logging.debug(Msg)
				else:
					Msg = u"抓取图片失败，原因：%s " % img.status_code
					# print Msg
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
							# print Msg
							logging.debug(Msg)
						else:
							Msg =  '100% 已下载 --（图片名：{1})'.format(img_filename)
							# print Msg
							logging.debug(Msg)

		except Exception ,e:
			Msg = "下载图片失败，原因：%s " % e
			# print Msg
			logging.debug(Msg)

	def get_big_img_and_type(self, small_img):
		"""返回大图地址，已经原图类型（main，normal）"""
		img_type = 'main' #默认设定原图是主图
		#th替换成i
		big_img_re_str = r'/th/'
		big_img_re =re.compile(big_img_re_str)
		big_img = re.sub(big_img_re,'/i/',small_img)
		response = requests.get(big_img)
		img_content_length = 0
		try:
			img_content_length = int(response.headers['content-length'])
		except Exception as e:
			Msg = u"小图（%s）的大图没有找到content_length！%s" % (small_img,e)

			wp_logging(Msg=Msg, allow_print=False)
			raise e
		if img_content_length == 8183: #一张错误图片，则原图是normal图片
			img_type = 'normal'
			#将 jpg替换成 jpeg
			big_img_re_str = r'jpg$'
			big_img_re =re.compile(big_img_re_str)
			big_img = re.sub(big_img_re,'jpeg',big_img)
		return (big_img, img_type)

	def get_big_img_imgspice(self,small_img):
		#imgspice.com
		img_name = small_img.get('img_name')
		img_ext = small_img.get('img_ext')
		small_img = small_img.get('img_url')
		if img_ext == '.jpeg':
			big_img = small_img[:-5]+u'_t.jpg'
		else:
			big_img = small_img[:-6]+u'.jpeg'

		# print "imgspice big_img url-1: %s" % big_img
		response = requests.get(big_img)
		img_content_length = 0
		try:
			img_content_length = int(response.headers['content-length'])
		except Exception as e:
			Msg = u"大图没有找到content_length！%s" % e
			wp_logging(Msg=Msg)
		if img_content_length == 40275: #一张错误图片，则原图是normal图片
			#将 jpeg替换成 jpg
			big_img_re_str = r'jpeg$'
			big_img_re =re.compile(big_img_re_str)
			big_img = re.sub(big_img_re,'jpg',big_img)

		return (big_img,)

	def grab_article_url(self,page_start=1,page_end=1):
		'''
		计算待抓取的所有页面，存在一个列表里，并传递给一个线程池
		'''
		page_number_list = [page_number for page_number in range(page_start,page_end+1)]

		#同时抓取多少网页的文章URL
		pool = ThreadPool(1)
		try:
			pool.map(self.grab_article_url_of_per_page, page_number_list)
		except Exception,e:
			Msg = u'抓取文章链接错误：%s' % e
			wp_logging(Msg=Msg,allow_print=False)

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
			Msg = u'链接到网页失败：%s ' % e
			wp_logging(Msg=Msg)
			return


		if r.status_code is not 200:
			Msg = "首页抓取不是200,返回状态码：" + str(r.status_code)
			wp_logging(Msg=Msg)
			return

		h = pq(r.text)
		article_urls_htmlelements = h('.more-link')

		for article_url in article_urls_htmlelements:
			article_url_ = article_url.attrib['href'].split("#")[0]
			article_urls.append(article_url_)

		return article_urls


	def grab_article(self,name='',url=''):
		id = url.split('/')[-1].split('.')[0]
		file_dir = os.path.dirname(os.path.abspath(__file__)) + '/articles/filmav/grabed_articles/'+str(date.today()).replace('-','_') + '/'
		id_blocked_file =  os.path.dirname(os.path.abspath(__file__)) + '/articles/filmav/id_blocked.txt'
		id_blocked_list = []

		with open(id_blocked_file) as f:
			for line in f.readlines():
				id_blocked_list.append(line.strip('\n'))
		if id in id_blocked_list:
			return
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)
		file_path =  file_dir + id + '.py'
		if os.path.exists(file_path) and os.stat(file_path) !=0:
			print 'alread exist'
			return



		print u'开始抓取url: %s' % url
		r = requests.get(url, headers=self.headers)
		h = pq(r.content)
		body = h('.entry')
		old_body_str =body.html()

		body_dict = {}
		#抓取主体
		old_body = re.split(u'<span style="color: #ff0000;"><strong>Premium Dowload ゴッド会員 高速ダウンロード',old_body_str)
		old_body = old_body[0]
		#抓取描述
		pattern_str1 = u'<a.*.</a>'
		pattern_str2 = u'<p><span class="wp_keywordlink_affiliate">.*.<br />|'
		pattern_str3 = u'<strong><span id="more.*.'

		pattern1 = re.compile(pattern_str1)
		pattern2 = re.compile(pattern_str2)
		pattern3 = re.compile(pattern_str3,re.DOTALL)

		description = re.sub(pattern1,'',old_body_str)
		description = re.sub(pattern2,'',description)
		description = re.sub(pattern3,'',description)
		description = description.strip().strip('<br />').strip('\n')
		# print 'description:%s' % description
		#抓取文章标题
		title = h('.title-single')
		title_unicode = unicode(title.html())
		title_str = title.html()
		# print 'title: %s' % title_str
		body_dict.update({'title':title_str})
		#抓取所有图片,使用非贪婪模式
		#图片网站1
		small_img_re_str = r'(?P<images>http://img[\d]{0,3}.imagetwist.com/.*?.jpg)'
		small_img_re = re.compile(small_img_re_str)
		small_imgs = re.findall(small_img_re, old_body_str)
		# if not small_imgs:
		# 	print '='*99
		# 	print u'%s 没有找到imagetwist图片' % url
		# 	print '='*99
		# 封面图 small_imgs[0]
		cover_img = small_imgs[0]
		Msg = u'cover_img:%s' % cover_img
		wp_logging(Msg=Msg)
		screenshosts = []
		for small_img in small_imgs[1:]:
			# screenshots
			img_name = small_img.split('/')[-1]
			big_img, img_type = self.get_big_img_and_type(small_img=small_img)
			screenshosts.append(big_img)

		#图片网站2
		small_img_re_str = r'(?P<img_url>(?P<img>http://img[\d]{0,3}.imgspice.com/i/[0-9]*/)(?P<img_name>.*?(?P<img_ext>.jpe?g)))'
		small_img_re = re.compile(small_img_re_str)
		small_imgs = re.finditer(small_img_re, old_body_str)
		small_imgs_dict = [ m.groupdict() for m in small_imgs]

		for small_img in small_imgs_dict:
			"""
			small_path--> 图片存于small_path,
			big_path-->图片存于big_path
			"""
			# print 'imgspice图片%s' % small_img
			img_name = small_img.get('img_name')
			img_ext = small_img.get('img_ext')
			small_img_url = small_img.get('img_url')

			big_img = self.get_big_img_imgspice(small_img)[0]
			screenshosts.append(big_img)
		# print 'screenshosts %s' % screenshosts
		body_dict.update({'screenshosts':screenshosts})
		#todo 抓取文章发布时间
		pre_posted_date = h('.post-info-date').text()
		pre_posted_date_list = re.split(',| ',pre_posted_date)
		t_str = pre_posted_date_list[-4][:3] +' '+ pre_posted_date_list[-3] + ' ' + pre_posted_date_list[-1]
		pre_posted_date = datetime.strptime(t_str, '%b %d %Y')

		#todo 抓取作者，拍摄电影的俱乐部
		#抓取电影分类
		categories = h('a[rel="category tag"]')
		categories_text_list = []
		categorys = '['
		categorys_temp_list = []
		for category in categories:
			if category is not None:
				category_text = unicode(category.text).decode('utf8')
				categories_text_list.append(category_text)
				if category not in categorys_temp_list:
					categorys_temp_list.append(category)
					categorys +="'%s'," % category
			categorys+=']'
		# print "categories %s " % categories_text_list

		body_dict.update({'categories':categories})
		#抓取tag,使用非贪婪模式
		tags_re_str = r'tag/.*?>(.*?)</a>'
		tags_re = re.compile(tags_re_str)
		tags_finded = re.findall(tags_re, old_body_str)
		tags = '['
		tags_temp_list = []

		for tag in tags_finded:
			# tag =  tag.encode('utf8')
			# print tag
			if tag not in tags_temp_list:
				tags_temp_list.append(tag)
				tags +="u'%s'," % tag
		tags+=']'

		# print 'tags %s' % tags_temp_list
		body_dict.update({'tags':tags})

		old_download_link_pattern = r'(http://ryushare.com/.*/.*)" target="_blank"?'
		old_download_link = self.grap_download_links(pattern=old_download_link_pattern,old_body_str=old_body_str)
		if not old_download_link:
			old_download_link_pattern = r'(http://www.datafile.com/.*/.*)" target="_blank"?'
			old_download_link = self.grap_download_links(pattern=old_download_link_pattern,old_body_str=old_body_str)
		file_name = name
		# try:
		# 	file_name = old_download_link.split('/')[-1].split('.')[0].replace(' ','_').replace('-','_')
		# 	wait_to_uploaded_url.append(url)
		# except:
		# 	with open(id_blocked_file,'a') as f:
		# 		f.write(id+'\n')
		# 		f.flush()
		# 	return
		# print 'file_name: %s ' % file_name
		body_dict.update({'file_name':file_name})




		with codecs.open(file_path,'wb',encoding='UTF-8') as f:

			new_body={
				'id':id,
				'file_name':file_name,
				'description':description,
				'cover_img':cover_img,
				'screenshosts':screenshosts,
				'categories':categories_text_list,
				'tags':tags_temp_list,

			}
			json.dump(new_body,f)
# 			body = u'''# -*- coding:utf-8 -*-
# {file_name} = {left_b}
# 	'title':'u{title}',
# 	'description':u{three_sq}{description}{three_sq},
# 	'cover_img':u'{cover_img}',
# 	'screenshosts':{screenshosts},
# 	'categories':{categories},
# 	'tags':{tags},
# 	'file_name':u'{file_name}',
# {right_b}
# '''.format(file_name=file_name,title=title_str,description=description,cover_img=cover_img,categories=categories_text_list, \
# 				screenshosts=screenshosts,tags=tags,left_b='{',right_b='}',three_sq='\'\'\'')
# 			# f.write(body)
# 			f.write(new_body)
# 			f.flush()
# title=str(title_str.encode('utf8'))
	def grap_download_links(self,pattern='',old_body_str =''):
		# wp_logging(Msg=u"开始抓取old download links", allow_print=True)
		old_download_links_re_str = pattern
		old_download_links_re = re.compile(old_download_links_re_str)
		old_download_links = re.findall(old_download_links_re, old_body_str)
		for old_download_link in old_download_links:
			# print u"下载链接 %s" % old_download_link
			return old_download_link





	def post_to_wordpress_system(self,article):
		post_tag_list = []
		category_list = []
		wp_client = Client('http://jpnewfilm.com/xmlrpc.php', 'jpadmin', 'qQ2@wW')

		post = WordPressPost()
		post.title = article.title
		post.content = article.body_wordpress
		post.post_status = 'publish'
		post.terms_names = {
		  'post_tag': post_tag_list,
		  'category': category_list,

		}
		try:
			post_time = datetime.today()
			result = wp_client.call(NewPost(post))
		except Exception as e:
			Msg = u'@@@发布文章%s 有错误！（errmsg：%s)' % (article.id, e)
			wp_logging(Msg=Msg)



if __name__ == '__main__':

	filmav_grab = Filmav_Grab()
	# url = 'http://filmav.com/60696.html'
	#
	# filmav_grab.grab_article(url=url)

	if True:
		# urls = filmav_grab.grab_article_url_of_per_page(page_number=1)
		urls_file_path = os.path.dirname(os.path.abspath(__file__)) + '/articles/filmav/urls_temp.txt'
		urls_dict = {}
		with open(urls_file_path,'r') as f:
			for line in f.readlines():
				name, url = line.strip().split(',')
				urls_dict.update({name:url})
		# print urls_dict
		for name, url in urls_dict.iteritems():
			filmav_grab.grab_article(name=name,url=url)
		exit()
		# for i in range(0,len(urls)):
		# 	url = urls.pop(0)
		# 	filmav_grab.grab_article(url=url)
		#保存需要手动去获得下载地址的url
		# urls_file_path = os.path.dirname(os.path.abspath(__file__))+'/articles/'+str(date.today())
		# with open(urls_file_path, 'wb') as f:
		# 	for url in wait_to_uploaded_url:
		# 		url_html = "<a href='{url}' >{url} </a>\r\n<br />".format(url=url)
		# 		f.writelines(url_html)
		# 		f.flush()

