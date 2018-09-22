#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/1 15:23
# @Author  : DollA
# @Site    : 
# @File    : file_func.py
# @Software: PyCharm
import hashlib
from core import progress_bar


class File_Func:
    """
    文件操作
        上传
        下载

    """

    def __init__(self, file_name, conn, open_model, **kwargs):
        self.file_name = file_name
        self.conn = conn
        self.open_model = open_model
        self.kwargs = kwargs

    # 文件哈希
    def file_md5_hash(self):
        with open(self.file_name, self.open_model) as f:

            f.seek(0)
            md5 = hashlib.md5()
            while True:
                data = f.read(1024)
                if not data: break
                md5.update(data)
            return md5.hexdigest()

    # 发送文件
    def send_file(self):
        with open(self.file_name, self.open_model) as f:
            # 生成进度条对象
            progress_bar_generator = progress_bar.progress_bar(self.kwargs['file_size'], current_percent=0,
                                                               last_percent=0)
            progress_bar_generator.__next__()

            f.seek(self.kwargs['sended_size'])
            for line in f:
                line_len = len(line)
                self.conn.send(line)
                self.kwargs['sended_size'] += line_len
                progress_bar_generator.send(self.kwargs['sended_size'])


            else:
                print('文件发送成功')
                return True

    # 接收文件
    def get_file(self):
        with open(self.file_name, self.open_model) as f:

            # 生成进度条对象
            if self.kwargs['recv_data'] > 0:
                progress_bar_generator = progress_bar.progress_bar(self.kwargs['file_size'],
                                                                   current_percent=self.kwargs['current_percent'],
                                                                   last_percent=self.kwargs['current_percent'])
            else:
                progress_bar_generator = progress_bar.progress_bar(self.kwargs['file_size'], current_percent=0,
                                                                   last_percent=0)
            progress_bar_generator.__next__()

            while self.kwargs['recv_data'] < self.kwargs['file_size']:
                if self.kwargs['file_size'] - self.kwargs['recv_data'] < 8192:
                    data = self.conn.recv(self.kwargs['file_size'] - self.kwargs['recv_data'])
                else:
                    data = self.conn.recv(8192)
                self.kwargs['recv_data'] += len(data)
                f.write(data)
                progress_bar_generator.send(self.kwargs['recv_data'])

            else:
                return True
