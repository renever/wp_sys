# -*- coding:utf-8 -*-
import os
import humanize
# import sys
# sys.path.append('/home/l/app/learning/wangpan/')

from utility.common import create_session, common_utility
from models import Article,OldDownloadLink
from sqlalchemy.sql import func
from sqlalchemy.orm import contains_eager, subqueryload
from sqlalchemy import literal

# s = os.path.getsize('/home/l/app/learning/wangpan/wp_resource/downloaded_files/chrome.part6_005.rar')
# s2 = os.path.getsize('/home/l/app/learning/wangpan/wp_resource/downloaded_files/chrome.part3.rar')
# print s
# h =  humanize.naturalsize(s2, gnu=True,format='%.2f')
# print h
# print type(h)
#
# def f1():
#     return ('a','b')
# a1,b1 = f1()
# print a1

def get_wait_to_download_urls():

	#实际情况，过滤条件改成含有未下载地址的，最新发布的一篇文章
	db_session = create_session()
	# article = db_session.query(Article).join(OldDownloadLink).filter('downloaded'==func.all(OldDownloadLink.status))
	# article2 = db_session.query(Article).join(OldDownloadLink).filter(literal('downloaded')==func.all(OldDownloadLink.status)).all()
	# article2 = db_session.query(Article).join(OldDownloadLink).filter(literal('downloaded')==OldDownloadLink.status).all()
	# article2 = db_session.query(Article).join(OldDownloadLink).filter('downloaded'==func.any(OldDownloadLink.status)).all()
	# article = db_session.query(Article).join(Article.old_download_links).filter(Article.old_download_links.any(status='downloaded')).all()
	# article = db_session.query(Article).join(Article.old_download_links).first()
	# article = db_session.query(Article).join(Article.old_download_links).options(contains_eager('old_download_links')).filter(OldDownloadLink.status=='downloaded').first()
	# article = db_session.query(Article).join(Article.old_download_links).filter(OldDownloadLink.status=='downloaded').first()
	# article = db_session.query(Article).join(OldDownloadLink).options(subqueryload(Article.old_download_links)).filter(OldDownloadLink.status=='downloaded').first()
	# article2 = db_session.query(Article).filter(Article.all_url_downloaded == '480')
	# # print article
	# print article2
	q = db_session.query(OldDownloadLink).filter(OldDownloadLink.article_id==1)
	# q = db_session.query(OldDownloadLink)
	# q.update({'status': 'unrared2'})
	#
	# # db_session.add(q)
	# db_session.commit()
	q.update({'status': 'unrared'})
	# q.update({'status': 'downloaded'})
	# q.update({'status': 'waiting_download'})
	db_session.commit()
	db_session.close()

# get_wait_to_download_urls()

# import shutil
# file_path = '/home/l/app/learning/wangpan/wp_resource/downloaded_files/chrome.part1.rar'
# dir = '/home/l/app/learning/wangpan/wp_resource/articles_file/123/downloaded_files'
# # shutil.move(,)
# common_utility.move_file_to_dir(file_path,dir)

# dir_path = '/home/lotaku/app/learning/wangpan/wp_resource/articles_file/1/unrared_files'
# l = os.listdir(dir_path)
# print type(l)
# print l
# new_l = []
# for name in l:
# 	try:
# 		print name.encode('utf8')
# 		ext = name.split('.')[1].lower()
# 		print ext.encode('utf8')
# 		if ext.encode('utf8') in ['avi','mp4','txt',u'未命名文件夹']:
#
# 			new_l.append(name.encode('utf8'))
# 	except:
# 		pass
# print new_l
dir_path = '/home/l/app/learning/wangpan/wp_resource/articles_file/1/rared_files'
for dirname, dirnames, filenames in os.walk(dir_path):
	# print path to all subdirectories first.
	for subdirname in dirnames:
		print os.path.join(dirname, subdirname)

	# print path to all filenames.
	for filename in filenames:
		print os.path.join(dirname, filename)

	# Advanced usage:
	# editing the 'dirnames' list will stop os.walk() from recursing into there.
	if '.git' in dirnames:
		# don't go into any .git directories.
		dirnames.remove('.git')