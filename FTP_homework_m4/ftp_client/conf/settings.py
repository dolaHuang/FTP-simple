#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/14 15:45
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
address_family = socket.AF_INET  # socket家族 ，基于网络的链接
socket_type = socket.SOCK_STREAM  # 基于流式for tcp，socket.SOCK_DGRAM #for udp
allow_reuse_address = False  # 是否重用地址，默认不用
CODING = 'gbk'

# 日志目录
LOG_FILE = os.path.join(BASE_DIR, r'logs\log')
# 日志级别
LOG_LEVEL = logging.INFO
# 提示代码
STATUS_CODE = {
        200: '账号通过验证',
        201: '账号验证失败',
        202: '账号不存在',
        300: '文件不存在',
        301: '文件存在',
        302: '文件已经失效，无法继续下载',
        400: '目录不存在',
        401: '目录切换成功',
        500: '文件上传失败',
        501: '文件上传成功',
        600: '文件夹创建成功',
        601: '文件夹已存在'
    }
# 一次最大接受数据长度
MAX_PACKET_SIZE = 1024


