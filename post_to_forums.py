# -*- coding: utf-8 -*-
import os
import requests
from pyquery import PyQuery as pq

from pyquery import PyQuery as pq
import shutil
import json

class Forum1():
	'''
	抓取新的下载地址
	'''
	def __init__(self):
		self.forum_name = 'tvboxnow.com'
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
		self.session = requests.session()
		self.response = ''
	def login(self):
		login_page = self.session.get('http://www.tvboxnow.com/logging.php')
		h = pq(login_page.text)
		formhash = h('input[name="formhash"]')
		print formhash.attr['value']
		# <input type="hidden" name="formhash" value="46c39581" />


		# url = 'http://www.tvboxnow.com/logging.php?action=login&loginsubmit=yes&inajax=1'
		# data = {
		#
		# 	'login':	u'登录',
		# 	'password':	u'123qwe',
		# 	'username':	u'微微DE',
		# }
		#
		# self.response = self.session.post(url=url, data=data,)
		# print 'login status : %s' % self.response
	def run(self):
		self.login()
		# self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.response = self.session.post(url=self.url, data=self.data,)
		print 'post status : %s' % self.response


class Forum2():
	'''
	抓取新的下载地址
	'''
	def __init__(self):
		self.forum_name = 'powerapple.com'
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
			'Host': '',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
			'Accept-Encoding': 'gzip, deflate',
			# 'Referer': '',
		}
		self.session = requests.session()
		self.response = ''
	def login(self):
		login_page = self.session.get('http://bbs.powerapple.com/member.php?mod=logging&action=login')
		h = pq(login_page.text)
		form = h('form[name="login"]')
		url = 'http://bbs.powerapple.com/' + form.attr['action'] + '&inajax=1'
		formhash = h('input[name="formhash"]').attr['value']

		data = {
			'answer': u'',
			'formhash':	formhash,
			'password':	u'123qwe',
			'username':	u'sharemovieZN',
			'questionid':u'0',
			'referer':	'http://bbs.powerapple.com/./',
		}
		#
		self.response = self.session.post(url=url, data=data,)
		print 'login status : %s' % self.response
		print self.response.text
	def run(self):
		self.login()
		# self.response = self.r_session.post(url=self.url, data=self.data, headers=self.headers)
		self.response = self.session.post(url=self.url, data=self.data,headers=self.headers)
		print 'post status : %s' % self.response

if __name__ == '__main__':

	forum = Forum2()
	forum.login()

