# -*- encoding: utf-8 -*-
'''
@File    :   log_record.py
@Time    :   2020/04/04
@Author  :   Coder-Sakura
@Version :   1.0
@Desc    :   log
'''

# here put the import lib
import os
import sys
from loguru import logger
from config import DEBUG

if DEBUG:
    level = "DEBUG"
else:
    level = "INFO"

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
# remove default handler
logger.remove()
# 控制台输出
logger.add( 
    sys.stderr,
    level=level
)
# 日志写入
logger.add( 
    os.path.join(log_path, "{time}.log"),
    encoding="utf-8",
    rotation="00:00",
    enqueue=True,
    level=level
)


# def log_str(*args, end=None):
#     for i in args:
#         print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"),i),end=end)