#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/13 10:41
# @Author  : DollA
# @Site    : 
# @File    : Client.py
# @Software: PyCharm
import sys
import socket
import struct
import json
import os
import time
import shelve
import hashlib

from conf import settings
from core.logger import logger
from core.file_func import File_Func


# 客户端类
class FtpClient:

    def __init__(self):
        """
        生成套接字对象
        """
        self.terminal_display = None
        self.ftp_socket = socket.socket(settings.address_family, settings.socket_type)
        self.address = (settings.HOST, settings.PORT)
        self.make_connction()
        self.username = None
        self.shelve_obj = shelve.open('pending_download')
        self.current_dir = ''

    # 建立链接
    def make_connction(self):
        """
         链接服务端地址
        :return:
        """
        self.ftp_socket.connect(self.address)

    # 用户认证
    def auth(self):
        """
        设置发送数据格式
            字典格式{
                    命令类型
                    账号
                    密码
            }
        序列化数据
        套接字发送数据
        调用，接受返回数据方法，得到返回数据
            如果状态码是200，代表验证成功
                把用户名设置成公共调用方法，以后会用
                打印状态消息
                返回真
            如果是201
                打印状态消息
                返回假

        :return:
        """
        while True:
            action_type = 'auth'
            username = input('账号>>').strip()
            password = input('密码>>').strip()
            self.i_send(action_type=action_type, username=username, password=password)
            bytes_data = self.i_get_response()
            data = json.loads(bytes_data)
            if data['status_code'] == 200:
                print(settings.STATUS_CODE[200])
                # 日志
                msg = '用户%s登陆' % username
                logger(msg)
                # 把当前用户名存为属性，方便调用
                self.username = username
                # 保存一个输入框名称，实现类似随时显示当前目录的命令行
                self.terminal_display = r'%s' % self.username
                return True
            else:
                print('账号或者密码错误')

    # 获取返回信息
    def i_get_response(self):
        """
        1、直接获取
        2、根据头消息，设置接收数据长度，依次接收
                首先接收的是数据的长度

        反序列化
        返回接受的消息
        :return:
        """
        # 先接收消息头
        data_header = self.ftp_socket.recv(4)
        data_header_size = struct.unpack('i', data_header)[0]
        # 接收反馈消息，据此消息执行后面的额操作
        bytes_data = self.ftp_socket.recv(data_header_size)
        return bytes_data

    # 与客户端的交互
    def interaction(self):
        """
        验证账号
        如果验证成功
            提示用户输入指令，
            分析指令，调用相应方法

        :return:
        """
        # 验证账号
        if self.auth():
            print('欢迎%s'.center(40, '-') % self.username)
            # 检查是不是有没有完成的下载
            self.unfinished_file_check()
            # 要求输入指令
            while True:
                cmd = input('[%s]>>' % self.terminal_display).strip()
                cmd_list = cmd.split()
                if hasattr(self, 'i_%s' % cmd_list[0]):
                    func = getattr(self, 'i_%s' % cmd_list[0])
                    func(cmd_list[1:])
                else:
                    print('输入的指令不正确！请重新输入')
                    self.help()
        else:
            print('认证失败')

    # 显示帮助信息
    def help(self):
        hsg = {
            "put": "作用：上传文件，格式：put 文件名",
            "get": "作用：下载文件，格式：get 文件名",
            "dir": "作用：展示当前文件夹内容，格式：dir",
            "cd": "作用：切换文件夹，格式：cd 目标文件夹",
        }
        print('指令帮助信息'.center(40, '-'))
        for i in hsg:
            print(i, hsg[i])

    # 验证输入的参数是否合法
    def parameter_check(self, cmd_args, min_args=None, max_args=None, exact_args=None):
        """
        验证用户输入的指令，是否合法（参数够不够）

        """
        if min_args:
            if len(cmd_args) < min_args:
                print('最少需要%s个参数，您输入了%s个参数' % (min_args, len(cmd_args)))
                return False
            else:
                return True
        if max_args:
            if len(cmd_args) > max_args:
                print('对多需要%s个参数，您输入了%s个参数' % (max_args, len(cmd_args)))
                return False
            else:
                return True
        if exact_args:
            if len(cmd_args) != exact_args:
                print('必须提供%s个参数，您输入了%s个参数' % (exact_args, len(cmd_args)))
                return False
            else:
                return True

    # 打包消息，发送消息给服务端
    def i_send(self, *args, **kwargs):
        """
        定义消息格式，字典{
                        消息类型
                        数据
        }
        updata合并动态参数kwargs
        序列化数据
        根据数据长度，发送数据，解决粘包问题
        :param kwargs:
        :return:
        """
        # 序列化--->struct打包--->发送
        data_bytes = json.dumps(kwargs).encode()
        self.ftp_socket.send(struct.pack('i', len(data_bytes)))
        self.ftp_socket.send(data_bytes)

    # 下载文件
    def i_get(self, cmd_args):
        """
        调用检查参数方法
            如果合法
                发送命令类型，文件名字
                获取返回数据
                    如果状态码是301
                        提取文件名
                        选择保存路径
                        接受数据
                    
        :param cmd_args:
        :return:
        """
        # 发送请求到服务端
        if self.parameter_check(cmd_args, exact_args=1):
            file_name = cmd_args[0]
            self.i_send(action_type='get', file_name=file_name, username=self.username)
            # 接收到反馈
            bytes_data = self.i_get_response()
            data = json.loads(bytes_data)
            # 文件存在，开始下载
            # 先接收服务端文件的MD5值
            if data['status_code'] == 301:
                # 得到服务端MD5
                server_md5 = json.loads(self.i_get_response().decode())['md5_value']
                print('文件%s可以下载，共%sK' % (file_name, data['file_size']))
                # 如果文件名已存在，给新下载的文件名加上时间戳后缀
                if not os.path.exists(file_name):
                    file_path = file_name
                else:
                    file_path = '%s.%s' % (file_name, time.time())

                print('下载中......')
                # 文件功能对象
                file_func = File_Func('%s.download' % file_path, self.ftp_socket, 'wb', recv_data=0,
                                      file_size=data['file_size'])

                # 创建文件下载的临时信息,以文件的相对路径作为key,值包括：相对路径，文件大小
                file_abs_path = os.path.join(self.current_dir, file_name)
                self.shelve_obj[file_abs_path] = ['%s.download' % file_path,
                                                  data['file_size']]

                file_res = file_func.get_file()
                if file_res:
                    print('文件%s下载成功' % file_path)
                    # 日志
                    msg = '用户%s下载文件%s' % (self.username, file_path)
                    logger(msg)
                    # 删除临时文件信息
                    os.replace('%s.download' % file_path, file_path)
                    del self.shelve_obj[file_abs_path]

                    file_func_md5 = File_Func(file_path, self.ftp_socket, 'rb')
                    recv_md5 = file_func_md5.file_md5_hash()
                    if recv_md5 == server_md5:
                        print('下载的文件%s通过MD5校验' % file_path)
                        msg = '下载的文件%s通过MD5校验' % file_path
                        logger(msg)
                    else:
                        print('文件校验失败，请重新下载')
                else:
                    print('文件下载失败')

            else:
                print('文件%s不存在，下载失败' % file_name)

    # 查看目录
    def i_dir(self, cmd_args):
        """
        发送
        接受
        转码
        打印
        :return:
        """
        self.i_send(action_type='dir', username=self.username)
        dir_data = self.i_get_response()
        print(dir_data.decode('gbk'))
        # 日志
        msg = '用户%s查看当前目录' % self.username
        logger(msg)

    # 切换目录
    def i_cd(self, cmd_args):
        if self.parameter_check(cmd_args, exact_args=1):
            self.i_send(action_type='cd', cd_path=cmd_args[0], username=self.username)
            response = json.loads(self.i_get_response().decode())

            if response.get('status_code') == 401:
                self.terminal_display = '%s%s' % (self.username, response['current_dir'])
                # 切换路径，并得到在服务端的当前路径，用于下载文件，和断点续传可以在服务端找到文件路径
                self.current_dir = response.get('current_dir')
                # 日志
                msg = '用户%s切换目录到%s' % (self.username, self.current_dir)
                logger(msg)
            # 目录不存在，打印错误信息
            elif response['status_code'] == 400:
                print(settings.STATUS_CODE[400])

    # 上传文件
    def i_put(self, cmd_args):
        """
        检测参数
        检测路径
            文件名，文件大小
            发送消息头
        发送文件
        接受反馈
        :return:
        """
        if self.parameter_check(cmd_args, exact_args=1):
            file_name = cmd_args[0]
            try:
                file_size = os.path.getsize(file_name)
                if os.path.isfile(cmd_args[0]):
                    self.i_send(action_type='put', file_name=file_name, file_size=file_size, username=self.username)

                    file_func = File_Func(file_name, self.ftp_socket, 'rb', sended_size=0, file_size=file_size)
                    file_res = file_func.send_file()
                    client_md5 = file_func.file_md5_hash()
                    if file_res:
                        print('文件上传成功')
                        # 接收服务端已上传文件MD5值
                        data = self.i_get_response()
                        server_md5 = json.loads(data.decode())['server_md5']
                        if server_md5 == client_md5:
                            print('上传到服务端的文件%s,MD5值校验成功' % file_name)
                            # 日志
                            msg = '用户%s上传文件到服务器，并校验成功' % self.username
                            logger(msg)

                else:
                    print('找不到该文件')
            except Exception as e:
                print('Error:', e)

    # 检查是否有未完成的下载
    def unfinished_file_check(self):
        """
        遍历未完成下载
        显示序号，文件名，下载百分比
        选择要继续下载的文件
        向服务端发出请求
        得到请求
            如果文件还在，开始下载

        :return:
        """
        while self.shelve_obj.keys():
            print('未完成下载列表'.center(40, '-'))

            for i, v in enumerate(self.shelve_obj.keys(), 1):
                received_size = os.path.getsize(self.shelve_obj[v][0])
                print(i, self.shelve_obj[v][0], '%s%s' %
                      (int(received_size / self.shelve_obj[v][1] * 100), '%'))

                choice = input('请选择需要继续下载的文件>>').strip()
                if choice.isdigit():
                    choice = int(choice)
                    if 0 < choice <= len(self.shelve_obj.keys()):
                        # 未完成的文件路径，也是shelve的key
                        choice_file = list(self.shelve_obj.keys())[choice - 1]
                        received_size = os.path.getsize(self.shelve_obj[choice_file][0])
                        file_size = self.shelve_obj[choice_file][1]
                        # 发送未下载完成的文件的信息给服务端
                        self.i_send(action_type='breakpoint_resume',
                                    file_path=choice_file,
                                    received_size=received_size,
                                    file_size=file_size,
                                    username=self.username)
                        # 接受反馈
                        response = json.loads(self.i_get_response())
                        if response.get('status_code') == 301:
                            file_download_path = self.shelve_obj[choice_file][0]
                            # 下载
                            res = self.i_breakpoint_resume(file_download_path, received_size, file_size)
                            if res:
                                print('文件下载成功')
                                file_new_name = file_download_path.strip('.download')
                                os.renames(file_download_path, file_new_name)
                                del self.shelve_obj[choice_file]
                                server_md5 = json.loads(self.i_get_response().decode())['server_md5']
                                file_func = File_Func(file_new_name, self.ftp_socket, 'rb')
                                client_md5 = file_func.file_md5_hash()
                                if server_md5 == client_md5:
                                    print('文件校验成功')
                                    # 日志
                                    msg = '完成未下载文件%s断点续传,并校验成功' % file_new_name
                                    logger(msg)
                                    break
                                else:
                                    print('文件校验失败')
                                    # 日志
                                    msg = '完成未下载文件%s断点续传,并校验失败' % file_new_name
                                    logger(msg)
                                    break
                            else:
                                print('文件断点续传失败')
                        else:
                            print(settings.STATUS_CODE[302])
                    else:
                        print('不存在的序号，请重新上输入')
                elif choice == 'q':
                    print('返回上一级')
                    break
                else:
                    print('输入错误，请重新输入')

    # 断点续传的继续下载方法函数
    def i_breakpoint_resume(self, file_download_path, received_size, file_size):
        """
        保存没有传输成功的文件
            1、文件名，2、文件路径，3、文件大小
        检测是否有未下载完的文件
            选择继续下载
                把文件信息和已下载大小发给服务器
                    找到了

                    没找到
                获得返回值
                继续下载
                修改文件名
            不下载
                删除本地文件
            重新下载
                删除本地文件
                把文件信息发给服务器
                获得返回值
                继续下载
        :return:
        """

        current_percent = int(received_size / file_size * 100)  # 已接收的百分比

        print('下载中......')
        file_func = File_Func(file_download_path, self.ftp_socket, 'ab',
                              recv_data=received_size,
                              file_size=file_size,
                              current_percent=current_percent,
                              last_percent=current_percent)
        file_res = file_func.get_file()
        return file_res

    # 新建文件夹
    def i_mkdir(self, cmd_args):
        """
        增加目录
            1，server返回1 增加成功
            2，server返回2 增加失败
         :param cmds:
         :return:
        :param cmd_args:
        :return:
        """
        if self.parameter_check(cmd_args, exact_args=1):
            self.i_send(action_type='mkdir', mk_path=cmd_args[0], username=self.username)
            response = json.loads(self.i_get_response().decode())
            if response.get('status_code') == 601:
                print('文件夹创建成功')
            else:
                print('文件夹创建失败')


if __name__ == '__main__':
    client = FtpClient()
    client.interaction()
