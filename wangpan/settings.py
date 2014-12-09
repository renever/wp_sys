# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence ,Text, String, Integer, ForeignKey , Boolean
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
import logging
import logging.config
import os
import pwd
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# print BASE_PATH
if pwd.getpwuid(os.getuid())[0]=='l':
	#XPS
	# DB_ENGINE = create_engine("mysql://root:123qwe@localhost/wangpan?charset=utf8",poolclass=NullPool,echo=True)
	DB_ENGINE = create_engine("mysql://root:123qwe@localhost/wangpan?charset=utf8", pool_size=300, max_overflow=1000,echo=True)
	# 					     # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句
	#浏览器配置地址
	#xps
	FirefoxProfilePath = '/home/l/.mozilla/firefox/mwad0hks.default'
	#图片文件目录
	# DOWNLOAD_DIR = BASE_PATH + 'downloaded_files/'
else:#公司PC
	#由于SQLite存在并发死锁，不再使用。# 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句
	# DB_ENGINE = create_engine("sqlite:///wangpan", echo=True)

	DB_ENGINE = create_engine("mysql://root:@localhost/wangpan?charset=utf8", pool_size=300, max_overflow=1000,echo=True)
	FirefoxProfilePath = '/home/lotaku/.mozilla/firefox/mwad0hks.default'

	# DOWNLOAD_DIR = '/home/lotaku/wangpan/downloaded_files'

DB_BASE = declarative_base()  # 生成了declarative基类, 以后的model继承此类

#图片文件目录
DOWNLOAD_DIR = BASE_PATH + '/wp_resource/downloaded_files'
ARTICLE_FILES_DIR = BASE_PATH + '/wp_resource/articles_file'
# print DOWNLOAD_DIR
if not os.path.exists(DOWNLOAD_DIR):
	os.mkdir(DOWNLOAD_DIR)

CHUNK_SIZE = 8192

#日志配置
logging_fileConfig_path = BASE_PATH + '/logging.conf'
logging.config.fileConfig(logging_fileConfig_path)
logger = logging.getLogger("wp")

#文件下载目录，级浏览器默认保存文件的地址



IMG_PATH = BASE_PATH + '/wp_resource/images'
if not os.path.exists(IMG_PATH):
	os.makedirs(IMG_PATH)
# 各种线程池大小
GRAB_ARTICLES_POOL_SIZE = 140

GRAB_ARTICLE_URL_POOL_SIZE = 200

SAVE_ARTICLE_URL_POOL_SIZE = 300

#temp

s_links = [
	'http://www.uploadable.ch/file/fKBAph49mgeh/chrome.part1.rar',
	'http://www.uploadable.ch/file/aKm6hXM2spDd/chrome.part2.rar',
	'http://www.uploadable.ch/file/eAJajDV5cJA4/chrome.part3.rar',
	'http://www.uploadable.ch/file/4DUm3RVUKzjr/chrome.part4.rar',
	'http://www.uploadable.ch/file/sFGNVYqEjCvu/chrome.part5.rar',
	'http://www.uploadable.ch/file/txPgQBDzY3HH/chrome.part6.rar',

	]

#全局变量：
DOWNLOAD_SYSTEM_IS_RUNNING = False

# 文件大小单位 ： 转换比率
FILE_UNIT_CONVERSION={
	'MB': 1048576,
	'KB': 1024,
}

#时区设置
os.environ['TZ'] = 'Asia/Shanghai'