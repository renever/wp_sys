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

def get_or_create(session, model, defaults=None, **kwargs):
	instance = session.query(model).filter_by(**kwargs).first()
	if instance:
		return instance, False
	else:
		# params = dict((k, v) for k, v in kwargs.iteritems())
		# params.update(defaults or {})
		instance = model(**kwargs)
		session.add(instance)
		return instance, True