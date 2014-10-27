# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence ,Text, String, Integer, ForeignKey , Boolean
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy import exc

engine = create_engine("mysql://root:123qwe@localhost/wangpan?charset=utf8",
					   echo=True)  # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句
Base = declarative_base()  # 生成了declarative基类, 以后的model继承此类

class Url(Base):
	__tablename__ = 'urls'
	id = Column(Integer,Sequence('url_id_seq'), primary_key=True)
	url = Column(String(255), unique=True)
	is_done = Column(Boolean, default=False)
	website = Column(String(255))

	def __init__(self,url,website):
		self.url = url
		self.website = website




article_tags = Table('article_tags', Base.metadata,
					  Column('article_id', Integer, ForeignKey('articles.id')),
					  Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Article(Base):
	__tablename__ = 'articles'
	website = Column(String(255))
	url = Column(String(255))
	title = Column(String(255))
	waite_download_list = Column(String(255))
	compelet_download_list = Column(String(255))
	is_posted = Column(Boolean, default=False)
	# many to many Article<->Tag
	tags = relationship('Tag', secondary=article_tags, backref='articles')

	title = Column(String(255))

class Tag(Base):
	__tablename__ = 'tags'

	id = Column(Integer, primary_key=True)
	tag = Column(String(50), nullable=False, unique=True)

	def __init__(self, Tag):
		self.keyword = Tag

Base.metadata.create_all(engine)

