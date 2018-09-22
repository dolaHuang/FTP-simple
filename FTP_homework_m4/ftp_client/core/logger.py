#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/19 20:49
# @Author  : DollA
# @Site    : 
# @File    : logger.py
# @Software: PyCharm
import logging

from conf import settings


def logger(msg):
    # 生成logging对象
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    # 生成handler 对象
    fh = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
    fh.setLevel(settings.LOG_LEVEL)
    # 生成 formatter 对象
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    # 绑定
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # 日志消息
    logger.info(msg)
    logger.removeHandler(fh)
    return logger
