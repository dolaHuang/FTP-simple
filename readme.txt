这是一个简单的FTP程序

一、程序功能
	1、必须验证通过才能使用程序，密码使用MD5加密处理
	2、支持多用户同时登陆（可以设置用户登录最大数量）
	3、客户端可以从服务端下载文件
	4、客户端可以向服务端上传文件
	5、用户可以查看服务端的目录文件
	6、用户可以在自己的家目录中切换目录
	7、对传输的文件进行MD5校验
	8、支持断点续传
	9、可以在当前目录新建文件夹
	
二、程序包含3个文件
	1、程序流程图
	2、程序代码
	3、readme

三、可使用用户
	账号pizza
	密码123456

四、程序树结构
│  
└─FTP_homework	程序根目录
    │  __init__.py
    │  
    ├─ftp_client	客户端目录
    │  │  __init__.py
    │  │  
    │  ├─bin		客户端启动目录
    │  │      start_client.py	客户端启动文件
    │  │      
    │  ├─conf	客户端配置文件
    │  │  │  config.ini
    │  │  │  settings.py	可配置参数
    │  │  │  __init__.py
    │  │          
    │  ├─core	程序主逻辑代码目录
    │  │  │  Client.py 客户端类
    │  │  │  file_func.py 文件操作模块
    │  │  │  logger.py 日志记录模块
    │  │  │  progress_bar.py 进度条功能模块
    │  │  │  __init__.py
    │  │  │  
    │  │  └─__pycache__
    │  │          Client.cpython-36.pyc
    │  │          file_func.cpython-36.pyc
    │  │          logger.cpython-36.pyc
    │  │          progress_bar.cpython-36.pyc
    │  │          __init__.cpython-36.pyc
    │  │          
    │  └─logs	日志目录
    │          log	日志文件
    │          __init__.py
    │          
    └─ftp_server	服务端目录
        │  __init__.py
        │  
        ├─bin 服务端启动目录
        │      start_server.py 服务端启动文件
        │      __init__.py
        │      
        ├─conf	服务端配置文件目录
        │  │  accounts.ini	账号文件
        │  │  settings.py	可配置参数文件
        │  │  __init__.py
        │  │  
        │  └─__pycache__
        │          settings.cpython-36.pyc
        │          __init__.cpython-36.pyc
        │          
        ├─core	服务端主逻辑代码
        │  │  auth.py 账号认证模块
        │  │  file_func.py 文件操作模块
        │  │  logger.py	日志记录模块
        │  │  Server.py	服务端类
        │  │  __init__.py
        │          
        ├─home	各用户空间家目录
        │  │  __init__.py
        │  │  
        │  ├─pizza	用户pizza的空间
        │  │  │  __init__.py
        │  │  │  
        │  │  ├─1
        │  │  │  │  1.jpg
        │  │  │  │  1.jpg.1530421222.4549491
        │  │  │  │  2.jpg
        │  │  │  │  
        │  │  │  ├─4
        │  │  │  └─6
        │  │  ├─2
        │  │  ├─3
        │  │  └─4
        │  └─shanshan	用户shanshan的空间
        │      │  __init__.py
        │      │  
        │      ├─1
        │      │      3.jpg
        │      │      4.jpg
        │      │      __init__.py
        │      │      
        │      └─2
        └─logs	日志目录
                log	日志文件
                __init__.py
                
