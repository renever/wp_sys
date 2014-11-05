# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence, Text, String, Integer, ForeignKey, Boolean
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy import exc

from settings import DB_ENGINE, DB_BASE


class CommonLink(DB_BASE):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), unique=True)
    is_done = Column(Boolean, default=False)
    website = Column(String(255))

    def __init__(self, url, website):
        self.url = url
        self.website = website





article_tag = Table('article_tags', DB_BASE.metadata,
                     Column('article_id', Integer, ForeignKey('articles.id')),
                     Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Article(DB_BASE):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    website = Column(String(255))
    # url = Column(String(255))
    title = Column(String(255))
    # old_download_links = Column(String(255))
    # new_download_links = Column(String(255))
    is_posted = Column(Boolean, default=False)
    # many to many Article<->Tag
    tags = relationship('Tag', secondary=article_tag, backref='articles')

    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child", backref=backref("parent", uselist=False))
    article_id = Column(Integer, ForeignKey('articles.id'))
    article = relationship(Article, backref=backref('article_link', order_by=id))



class Tag(DB_BASE):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

class ArticleLink(CommonLink):
    __tablename__ = 'article_links'

    have_crawled = Column(Boolean, default=False)


    def __init__(self,url,website):
        super(CommonLink,self).__init__()
        self.url = url
        self.website = website



class OldDownloadLink(CommonLink):
    __tablename__ = 'old_download_links'

    article_id = Column(Integer, ForeignKey('articles.id'))
    article = relationship(Article, backref=backref('old_download_links', order_by=id))


class NewDownloadLink(CommonLink):
    __tablename__ = 'new_download_links'

    article_id = Column(Integer, ForeignKey('articles.id'))
    article = relationship(Article, backref=backref('new_download_links', order_by=id))


if __name__ == '__main__':
    DB_BASE.metadata.create_all(DB_ENGINE)

