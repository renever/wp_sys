# -*- coding: utf-8 -*-
from settings import ENGING, BASE
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from models import Url
import spider

def create_session(engine, base):
	Session = sessionmaker(bind=engine)  # 创建一个Session类
	session = Session()  # 生成一个Session实例

	return  session

session = create_session(ENGING, BASE)

# url = Url(url='http://www.baidu.com')
#
# session.add(url)
# try:
# 	session.commit()
# except exc.IntegrityError, e :
# 	print "捕获异常： "+e.message

article_urls = spider.filmav_grab_article_url()

spider.filmav_save_article_url(article_urls=article_urls,session=session,Url=Url)