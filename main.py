# -*- coding: utf-8 -*-
from settings import DB_ENGINE, DB_BASE
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from models import FileLink
import spider
from utility import create_session


if __name__ == '__main__':
    session = create_session(DB_ENGINE, DB_BASE)

    article_urls = spider.filmav_grab_article_url()

    spider.filmav_save_article_url(article_urls=article_urls, session=session, model_url=FileLink)