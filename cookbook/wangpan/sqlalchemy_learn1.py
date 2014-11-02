# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence, String, Integer, ForeignKey
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy import exc

engine = create_engine("mysql://root:123qwe@localhost/wangpan",
					   echo=True)  # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句
Base = declarative_base()  # 生成了declarative基类, 以后的model继承此类


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, Sequence("user_id_seq"), primary_key=True)  # Sequence表示id自增长, 主键
	name = Column(String(50), unique=True)
	fullname = Column(String(50))
	password = Column(String(12))
	addresses = relationship("Address", backref="user", order_by="Address.id")

	def __init__(self, name, fullname, password):
		self.name = name
		self.fullname = fullname
		self.password = password

	def __repr__(self):
		return "<User('%s', '%s', '%s')>" % (self.name, self.fullname, self.password)


class Address(Base):
	__tablename__ = "addresses"

	id = Column(Integer, primary_key=True)
	email_address = Column(String(50), nullable=False)
	user_id = Column(Integer, ForeignKey("users.id"))  # Address表的外键是User表的主键 多个Address属于一个User(多对一)
	#
	# user = relationship("User", backref=backref('addresses', order_by=id))


	def __init__(self, email_address):
		self.email_address = email_address

	def __repr__(self):
		return "<Address('%s')>" % self.email_address  # <span></span> Base.metadata.create_all(engine)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)  # 创建一个Session类
session = Session()  # 生成一个Session实例

import time
t = int(time.time())
name = "wendy4" + str(t)
zhangsan = User(name, "zhangsan", "123qwe")
zhangsan.addresses = [
	Address(email_address="zhangsan@qq.com"),
	Address(email_address="zhangsan@163.com"),
]

session.add(zhangsan)
try:
	session.commit()
# except exc.IntegrityError, e :
except Exception, e:

	print e.__class__, e

from sqlalchemy import Table, Text

post_keywords = Table('post_keywords', Base.metadata,
					  Column('post_id', Integer, ForeignKey('posts.id')),
					  Column('keyword_id', Integer, ForeignKey('keywords.id'))
)


class BlogPost(Base):
	__tablename__ = 'posts'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	headline = Column(String(255), nullable=False)
	body = Column(Text)
	# many to many BlogPost<->Keyword
	keywords = relationship('Keyword', secondary=post_keywords, backref='posts')

	def __init__(self, headline, body, author):
		self.author = author
		self.headline = headline
		self.body = body

	def __repr__(self):
		return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


class Keyword(Base):
	__tablename__ = 'keywords'

	id = Column(Integer, primary_key=True)
	keyword = Column(String(50), nullable=False, unique=True)

	def __init__(self, keyword):
		self.keyword = keyword


from sqlalchemy.orm import backref
# "dynamic" loading relationship to User
BlogPost.author = relationship(User, backref=backref('posts', lazy='dynamic'))
Base.metadata.create_all(engine)

wendy = session.query(User). \
	filter_by(name=name). \
	one()
title = "%s's Blog Post" % name
post = BlogPost(title, "This is a test", wendy)
session.add(post)
keyword_1 = "wendy" + str(t)
keyword_2 = "firstpost" + str(t)
post.keywords.append(Keyword(keyword_1))
post.keywords.append(Keyword(keyword_2))
session.add(post)
session.commit()
print session.query(BlogPost).\
	filter(BlogPost.keywords.any(keyword=keyword_2)).\
	all()
