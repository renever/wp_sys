# -*- coding: utf-8 -*-


import os
import requests

from pyquery import PyQuery as pq
import shutil
import json

class PostTo6park():
	'''
	抓取新的下载地址
	'''
	def __init__(self):
		self.data = {
			'content':u'内容',
			'fid':u'',
			'password':u'123qwe',
			'rename':u'0',
			'rootid':'13292053',
			'subject':u'标题',
			'submit':u'确认发布',
			'uptid':u'主贴ID',
			'username':'u微微DE',
		}
		self.url = ''

		self.headers = {
			'Host': 'www.cool18.com',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
			'Accept-Encoding': 'gzip, deflate',
			'Referer': 'http://www.cool18.com/bbs5/index.php?app=forum&act=threadview&tid=13292053',
		}
		self.r_session = requests.session()
		self.response = ''
	def login(self):
		url = 'http://home.6park.com/index.php?app=login&act=dologin'
		data = {

			'login':	u'登录',
			'password':	u'123qwe',
			'username':	u'微微DE',
		}

		self.response = self.r_session.post(url=url, data=data,)
		print 'login status : %s' % self.response
	def run(self):
		self.login()
		# self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.response = self.r_session.post(url=self.url, data=self.data,)
		print 'post status : %s' % self.response
if __name__ == '__main__':

	post_to_6park = PostTo6park()

