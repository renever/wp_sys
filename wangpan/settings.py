# -*- coding: utf-8 -*-

from sqlalchemy import Column, Sequence ,Text, String, Integer, ForeignKey , Boolean
from sqlalchemy import create_engine  # 导入创建连接驱动
from sqlalchemy.ext.declarative import declarative_base
import logging
import logging.config
import os
BASE_PATH = os.path.dirname('__file__')
#XPS
# DB_ENGINE = create_engine("mysql://root:123qwe@localhost/wangpan?charset=utf8",
# 					   echo=True)  # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句

DB_ENGINE = create_engine("sqlite:///wangpan",
					   echo=True)  # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句

#公司电脑
# DB_ENGINE = create_engine("mysql://root:@localhost/wangpan?charset=utf8",
# 					   echo=True)  # 这个url可以用urlparse解析, 其中echo=True表示执行时显示sql语句

DB_BASE = declarative_base()  # 生成了declarative基类, 以后的model继承此类


CHUNK_SIZE = 8192

#日志配置
logging_fileConfig_path = BASE_PATH + 'logging.conf'
logging.config.fileConfig(logging_fileConfig_path)
logger = logging.getLogger("wp")

#图片文件目录

IMG_PATH = BASE_PATH + 'wp_resource/STATIC_FILES/images'