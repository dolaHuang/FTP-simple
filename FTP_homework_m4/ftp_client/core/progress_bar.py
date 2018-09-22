#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/1 21:31
# @Author  : DollA
# @Site    : 
# @File    : progress_bar.py
# @Software: PyCharm
import sys

# 打印进度条
def progress_bar(total_size, current_percent=0, last_percent=0):
    """
    把当前接收的大小传给yield
    计算当前已接受百分比
    如果当前百分比大于上一次的百分比
        打印相应个数的=（print，每次从头打印，立即把内容输出）
    把当前百分比赋值给上一次百分比

    :param total_size:
    :return:
    """
    while True:
        recv_size = yield current_percent
        current_percent = int(recv_size / total_size * 100)
        if current_percent > last_percent:
            if current_percent == 100:
                r = '\r%s>%s\n' % ('=' * int(current_percent / 2), current_percent)
            else:
                r = '\r%s>%s' % ('=' * int(current_percent / 2), current_percent)
            sys.stdout.write(r)
            sys.stdout.flush
        last_percent = current_percent