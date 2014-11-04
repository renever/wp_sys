# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence ,Text, String, Integer, ForeignKey , Boolean
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.ext.declarative import declarative_base


DB_ENGINE = create_engine("mysql://root:123qwe@localhost/wangpan?charset=utf8",
					   echo=True)  # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句
DB_BASE = declarative_base()  # 生成了declarative基类, 以后的model继承此类
