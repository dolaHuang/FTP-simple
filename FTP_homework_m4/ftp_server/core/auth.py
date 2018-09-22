#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/1 10:27
# @Author  : DollA
# @Site    : 
# @File    : auth.py
# @Software: PyCharm
import os
import hashlib
import configparser
from conf import settings
from core.logger import logger


class Auth:

    def __init__(self):
        self.accounts = self.load_accounts()
        self.user_obj = None
        self.user_current_dir = None

    # 加载账号信息
    def load_accounts(self, *args, **kwargs):
        """
        提取所有账号数据并返回（ini）
        加载到类属性中,方便调用
        :return:
        """
        config_obj = configparser.ConfigParser()
        config_obj.read(settings.ACCOUNT_FILE)
        return config_obj

    # 验证账号密码是否正确
    def authenticate(self, data):
        """
        接收的账号在账号数据中
            提取账号的MD5加密密码
            MD5加密接收数据中的密码

            如果相等，
                生成一个当前链接客户端对象
                赋值给用户数据
                添加家目录路径
                返回真
            不相等，返回假
        找不到数据，返回假
        :param data:
        :return:
        """
        if data['username'] in self.accounts:
            _password = self.accounts[data['username']]['password']

            md5 = hashlib.md5()
            md5.update(data['password'].encode())
            md5_password = md5.hexdigest()
            if _password == md5_password:
                print(settings.STATUS_CODE[200])
                # 日志
                msg = '用户%s成功登陆' % data['username']
                logger(msg)
                # 设置用户数据，用户家目录，用户当前目录为公共属性，方便调用
                self.user_obj = self.accounts[data['username']]
                self.user_obj['home'] = os.path.join(settings.USER_HOME_DIR, data['username'])
                self.user_current_dir = self.user_obj['home']

                return True
            else:
                print(settings.STATUS_CODE[201])
                return False
        else:
            print(settings.STATUS_CODE[202])
            return False




