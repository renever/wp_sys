# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
from sqlalchemy import exc


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
	filmav_grab_article_body()


