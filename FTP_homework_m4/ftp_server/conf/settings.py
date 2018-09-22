#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/13 20:00
# @Author  : DollA
# @Site    : 
# @File    : settings.py
# @Software: PyCharm
import os
import socket
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = '127.0.0.1'
PORT = 8085
ADDRESS_FAMILY = socket.AF_INET  # socket家族 ，基于网络的链接
SOCKET_TYPE = socket.SOCK_STREAM  # 基于流式for tcp，socket.SOCK_DGRAM #for udp
ALLOW_REUSE_ADDRESS = True  # 是否重用地址，默认不用

CODING = 'gbk'
MAX_LISTEN_SOCKET = 5
# 用户的空间家目录根目录
USER_HOME_DIR = os.path.join(BASE_DIR, 'home')

ACCOUNT_FILE = '%s/conf/accounts.ini' % BASE_DIR

# 日志目录
LOG_FILE = os.path.join(BASE_DIR, r'logs\log')
# 日志级别
LOG_LEVEL = logging.INFO
# 提示码
STATUS_CODE = {
    200: '账号通过验证',
    201: '账号验证失败',
    202: '账号不存在',
    300: '文件不存在',
    301: '文件存在',
    302: '文件已经失效，无法继续下载',
    400: '目录切换成功',
    401: '目录不存在',
    500: '文件上传失败',
    501: '文件上传成功',
    600: '文件夹创建成功',
    601: '文件夹已存在'
}
# 一次最大接受数据长度
MAX_PACKKET_SIZE = 1024
# 最大连接数
MAX_CONNECTION_COUNT = 2
