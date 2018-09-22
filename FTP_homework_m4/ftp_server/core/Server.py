#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @time    : 2018/6/13 10:50
# @author  : dolla
# @site    :
# @file    : server.py
# @software: pycharm
import socket
import struct
import json
import subprocess
import os
import hashlib
import time
from threading import Thread
import queue

from conf import settings
from core.logger import logger
from core import auth
from core.file_func import File_Func


# 服务端
class FtpServer:

    def __init__(self):
        """
        生成套接字对象
        
        """
        self.ftp_sock = socket.socket(settings.ADDRESS_FAMILY, settings.SOCKET_TYPE)
        self.server_bind()
        self.server_activate()
        self.queue_server = queue.Queue(settings.MAX_CONNECTION_COUNT)
        self.client_objs = {}

    # 套接字绑定ip和端口
    def server_bind(self):
        """
        如果允许重用地址是真
            设置重用方法
        套接字绑定
        :return:n
        """
        if settings.ALLOW_REUSE_ADDRESS:
            self.ftp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ftp_sock.bind((settings.HOST, settings.PORT))

    # 激活服务器,设置最大连接数
    def server_activate(self):
        """
        挂起套接字，开始监听
        :return:
        """
        self.ftp_sock.listen(settings.MAX_LISTEN_SOCKET)

    # 从套接字获取请求和客户端地址
    def get_accept(self):
        """
        返回客户端的链接和地址
        :return:
        """
        return self.ftp_sock.accept()

    # 运行服务端
    def run_server(self):
        """
        显示已连接服务端地址，端口
            接收客户端链接请求，生成链接和地址
            打印，已连接客户端地址
            调用处理链接接受的数据方法handle
        :return:
        """
        print('服务器（%s:%s）已启动'.center(40, '-') % (settings.HOST, settings.PORT))
        while True:
            conn, self.addr = self.get_accept()
            print('客户端%s连接'.center(34, '-') % (self.addr,))
            # 日志
            msg = '链接到客户端%s' % (self.addr,)
            logger(msg)
            try:
                server_thread = Thread(target=self.handle, args=(conn,))
                self.queue_server.put(server_thread)
                server_thread.start()
            except Exception as e:
                print('错误', e)
                conn.close()
                self.queue_server.get()

    # 处理与接收的的所有指令
    def handle(self, conn):
        """
        接受指令
            如果是空，打印失去连接，结束当前链接，结束此次访问
            如果有数据，反序列化数据
                查看指令类型
                如果指令类型存在
                    拿到类型
                    调用指定函数方法

        :return:
        """

        while True:
            try:
                data_header = conn.recv(4)
                if not data_header:
                    conn.close()
                    self.queue_server.get()
                data = conn.recv(struct.unpack('i', data_header)[0])
                data_bytes = json.loads(data.decode())

                if data_bytes.get('action_type'):
                    # 日志
                    msg = '接收到客户端%s的指令%s' % ((self.addr,), data_bytes['action_type'])
                    logger(msg)

                    if hasattr(self, 'i_%s' % data_bytes['action_type']):
                        func = getattr(self, 'i_%s' % data_bytes['action_type'])
                        func(data_bytes, conn)
                else:
                    print('指令错误')
            except ConnectionResetError:
                print('链接断开')
                conn.close()
                self.queue_server.get()
                break

    # 处理客户端的账号认证
    def i_auth(self, data, conn):
        """
         认证成功，返回200
         认证失败。返回201
        :param data:
        :return:
        """
        auth_obj = auth.Auth()
        if auth_obj.authenticate(data):
            self.client_objs[auth_obj.user_obj['name']] = auth_obj
            self.i_send_response(conn, status_code=200)
        else:
            self.i_send_response(conn, status_code=201)

    # 返回结果给客户端
    def i_send_response(self, conn, *args, **kwargs):
        """
        返回结果包括，状态码，和其他数据
            定义返回数据的格式
            先判断数据的格式
                字典格式，{
                            状态码
                            其他数据
                }
        序列化数据
        结决粘包问题，发送数据
        :param status_code:
        :param args:
        :param kwargs:
        :return:
        """
        # 先发数据长度
        # 再发数据

        bytes_data = json.dumps(kwargs).encode()
        conn.send(struct.pack('i', len(bytes_data)))
        conn.send(bytes_data)

    # 给客户端发送文件
    def i_get(self, data, conn):
        """
        拿到文件名
        判断是否存在
            存在，
                返回状态码，+文件大小
                发送文件数据
            不存在，
                返回状态码
        :param data:
        :return:
        """
        file_name = os.path.join(self.client_objs[data['username']].user_current_dir, data['file_name'])

        if os.path.isfile(file_name):
            file_size = os.path.getsize(file_name)
            self.i_send_response(conn, status_code=301, file_size=file_size)


            file_func = File_Func(file_name, conn, 'rb', recv_size=0)
            md5_value = file_func.file_md5_hash()
            self.i_send_response(conn, md5_value=md5_value)
            file_func.send_file()
        else:
            self.i_send_response(conn, status_code=300)
            print(settings.STATUS_CODE[300])

    # 查看当前目录
    def i_dir(self, cmd_args, conn):
        """
        命令结果是bytes类型，直接发送
        :param cmd_args:
        :return:
        """
        print(cmd_args)
        dir_obj = subprocess.Popen('dir %s' % self.client_objs[cmd_args['username']].user_current_dir,
                                   shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = dir_obj.stdout.read()
        stderr = dir_obj.stderr.read()

        cmd_rest = stdout + stderr
        conn.send(struct.pack('i', len(cmd_rest)))
        conn.send(cmd_rest)
        print('查询结果已发送')
        # 日志
        msg = '用户%s查看当前目录' % self.client_objs[cmd_args['username']]
        logger(msg)

    # 切换目录,改变指定路径
    def i_cd(self, cmd_args, conn):
        """
        拼接路径
        1、判断路径是否存在
        2、
        :param cmd_args:
        :return:
        """
        cd_path = cmd_args.get('cd_path')
        # 已登录的当前对象
        current_user_obj = self.client_objs[cmd_args['username']]
        # 拼出完整路径
        full_path = os.path.abspath(os.path.join(current_user_obj.user_current_dir, cd_path))

        if os.path.isdir(full_path):
            # 如果目录以家目录为开头，才允许继续向前切换
            if full_path.startswith(current_user_obj.user_obj['home']):
                current_user_obj.user_current_dir = full_path
                relative_current_path = \
                    current_user_obj.user_current_dir.replace(current_user_obj.user_obj['home'], '')

                self.i_send_response(conn, status_code=401, current_dir=relative_current_path)
                print('目录切换成功')
                # 日志
                msg = '用户切换到目录%s' % full_path
                logger(msg)
            else:
                self.i_send_response(conn, status_code=400, current_dir='\\')
                print('目录切换失败')

        else:
            print(settings.STATUS_CODE[400])
            self.i_send_response(conn, status_code=400, current_dir='\\')
            print('目录切换失败')

    # 接受上传文件
    def i_put(self, cmd_args, conn):
        """
        拿到文件名和文件大小
        对比空间额度和文件大小

        检查文件名是否存在
            是，创建一个新文件加时间后缀
            没有，创建新文件
        接受数据
        :param cmd_args:
        :return:
        """
        if cmd_args.get('file_name'):
            file_name = cmd_args['file_name']
            # 当前目录+文件名拼接成服务端的额文件完整路径
            full_path = os.path.join(self.client_objs[cmd_args['username']].user_current_dir, file_name)

            if os.path.exists(full_path):
                save_name = '%s.%s' % (full_path, time.time())
            else:
                save_name = full_path

            file_func = File_Func(save_name, conn, 'wb+', recv_data=0, file_size=cmd_args['file_size'])
            flag = file_func.get_file()
            if flag:
                print('文件上传成功')
                file_func_md5 = File_Func(save_name, conn, 'rb')
                server_md5 = file_func_md5.file_md5_hash()
                self.i_send_response(conn, server_md5=server_md5)
                # 日志
                msg = '用户%s 在客户端%s 上传文件%s' % \
                      (self.client_objs[cmd_args['username']].user_obj['name'], (self.addr,), full_path)
                logger(msg)

    # 断点续传
    def i_breakpoint_resume(self, cmd_args, conn):
        """
        接收到 客户端的请求
            文件路径，已接收文件大小
        找到文件
            发送反馈给客户端
            打开，seek，发送
        :return:
        """
        print('客户请求的未完成文件信息', cmd_args)
        # 去掉传过来的文件名头部的\\,否则会拼出错误的路径
        file_name = cmd_args['file_path'].strip('\\')
        full_path = os.path.join(self.client_objs[cmd_args['username']].user_obj['home'], file_name)

        if os.path.isfile(full_path):
            file_size_all = os.path.getsize(full_path)
            # 确认一下还是不是原文件,原文件大小和现在的文件对比
            if file_size_all == cmd_args['file_size']:
                if file_size_all > int(cmd_args['received_size']):
                    print('文件存在，可以继续下载')
                    self.i_send_response(conn, status_code=301)
                    file_func = File_Func(full_path, conn, 'rb', recv_size=cmd_args['received_size'])
                    flag = file_func.send_file()
                    if flag:
                        # 日志
                        sever_md5 = file_func.file_md5_hash()
                        self.i_send_response(conn, server_md5=sever_md5)
                        msg = '客户端%s的用户%s完成文件%s的断点续传' % \
                              ((self.addr,), self.client_objs[cmd_args['username']].user_obj['name'], full_path)
                        logger(msg)
                else:
                    print('客户端文件错误，无法下载')
            else:
                print('服务端文件已失效，无法继续下载')
                self.i_send_response(conn, status_code=302)
        else:
            print('文件不存在')

    # 新建文件夹
    def i_mkdir(self, cmd_args, conn):
        """
        在当前目录下,增加目录
            1.查看目录名是否已经存在
            2.增加目录成功,返回 1
            2.增加目录失败,返回 0
        :param conn:
        :return:
        """
        print(cmd_args)
        mkdir_path = os.path.join(self.client_objs[cmd_args['username']].user_current_dir, cmd_args['mk_path'])
        if not os.path.exists(mkdir_path):
            os.mkdir(mkdir_path)
            print('文件夹创建成功')
            self.i_send_response(conn, status_code=601)
        else:
            print('文件夹已存在')
            self.i_send_response(conn, status_code=600)

