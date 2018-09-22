#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/13 10:20
# @Author  : DollA
# @Site    : 
# @File    : start_server.py
# @Software: PyCharm
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core.Server import FtpServer

if __name__ == '__main__':
    server = FtpServer()
    server.run_server()

