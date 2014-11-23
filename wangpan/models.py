# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence, Text, String, Integer, ForeignKey, Boolean
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy import exc

from settings import DB_ENGINE, DB_BASE




class CommonForum(DB_BASE):
	__abstract__  = True

	title = Column(String(255))
	url = Column(String(512))
	username = Column(String(255))
	password = Column(String(255))


class Forum(CommonForum):
	__tablename__ = 'forums'

	id = Column(Integer, primary_key=True, autoincrement=True)


class CommonLink(DB_BASE):
	__abstract__ = True

	file_name = Column(String(255))
	file_size = Column(String(255))
	url = Column(String(255), unique=True)
	is_done = Column(Boolean, default=False)
	website = Column(String(255))
	status = Column(String(255))#waiting_download,downloading,downloaded,unraring,unrared,raring,rared,uploading,uploaded
	linkbuck = Column(String(255))

	def __init__(self, url, website,file_name,file_size, status):
		self.url = url
		self.website = website
		self.file_name = file_name
		self.file_size = file_size
		self.status = status


class FileLink(CommonLink):
	"""
	用于保存文章的来源地址URL
	"""
	__tablename__ = 'file_links'

	id = Column(Integer, primary_key=True, autoincrement=True)
	is_crawled = Column(Boolean, default=False)


	def __init__(self,url,website):
		super(CommonLink,self).__init__()
		self.url = url
		self.website = website

class Object(DB_BASE):
	__abstract__ = True

	name = Column(String(255))

class Category(Object):
	__tablename__ = 'categories'

	id = Column(Integer, primary_key=True, autoincrement=True)

	def __init__(self,name):
		super(Category,self).__init__()
		self.name = name


article_tag = Table('article_tag', DB_BASE.metadata,
					 Column('article_id', Integer, ForeignKey('articles.id')),
					 Column('tag_id', Integer, ForeignKey('tags.id')),
					 # UniqueKeyConstraint('article_id', 'tag_id'),

)

article_forum = Table('article_forum', DB_BASE.metadata,
					 Column('article_id', Integer, ForeignKey('articles.id')),
					 Column('forum_id', Integer, ForeignKey('forums.id'))
)

article_category = Table('article_category',DB_BASE.metadata,
					 Column('article_id', Integer, ForeignKey('articles.id')),
					 Column('category_id', Integer, ForeignKey('categories.id'))
)

class Article(DB_BASE):
	__tablename__ = 'articles'
	id = Column(Integer,primary_key=True, autoincrement=True)
	website = Column(String(255))
	title = Column(String(255), unique=True)
	is_posted = Column(Boolean, default=False)
	unrar_times = Column(Integer,default=0)
	can_posted = Column(Boolean, default=False)
	body = Column(String(512)) #保存HTML文件路径，文章正文
	file_name = Column(String(255),unique=True) #以文件名为唯一值
	# many to many
	have_post_to = relationship('Forum', secondary=article_forum, backref='articles_is_posted')
	wait_post_to = relationship('Forum', secondary=article_forum, backref='articles_wait_to_post')

	tags = relationship('Tag', secondary=article_tag, backref='articles')

	file_link_id = Column(Integer, ForeignKey('file_links.id'))
	file_link = relationship(FileLink, backref=backref('file_link', order_by=id))

	categories = relationship('Category', secondary=article_category, backref='articles')

	#images 已经在定义在Images 类一对多。
	#OldDownloadLink 一对多
	#NewDownloadLink 一对多

	def __init__(self, title=''):
		self.title = title
		# super(Article, self).__init__(*args, **kwargs)

	def __unicode__(self):
		return self.file_name


class Tag(DB_BASE):
	__tablename__ = 'tags'
	id = Column(Integer, primary_key=True,autoincrement=True)
	name = Column(String(50), nullable=False, unique=True)

	def __init__(self, name):
		self.name = name





class OldDownloadLink(CommonLink):
	__tablename__ = 'old_download_links'

	id = Column(Integer, primary_key=True, autoincrement=True)
	article_id = Column(Integer, ForeignKey('articles.id'))
	article = relationship(Article, backref=backref('old_download_links', order_by=id))


class NewDownloadLink(CommonLink):
	__tablename__ = 'new_download_links'

	id = Column(Integer, primary_key=True, autoincrement=True)
	article_id = Column(Integer, ForeignKey('articles.id'))
	article = relationship(Article, backref=backref('new_download_links', order_by=id))

class Image(DB_BASE):
	__tablename__ = 'images'
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255))
	small_path = Column(String(255)) #小图路径
	big_path = Column(String(255)) #大图路径
	article_id = Column(Integer, ForeignKey('articles.id'))
	article = relationship(Article, backref=backref('images', order_by=id))
	img_type =  Column(String(255)) # 'main'-->文章主图，'normal' -->文章普通图片

if __name__ == '__main__':
	DB_BASE.metadata.create_all(DB_ENGINE)

