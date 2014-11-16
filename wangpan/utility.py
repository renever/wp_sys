# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
import logging

def create_session(engine, base):
	Session = sessionmaker(bind=engine)  # 创建一个Session类
	session = Session()  # 生成一个Session实例

	return session


def wp_logging(level='debug', Msg='Msg'):
	if level=='debug':
		print Msg
		logging.debug(Msg)
		return