# coding=utf8
"""
Create On 2020-04-04
@author: Coder_Sakura
Project: Pixiv_Crawler
"""
import time

def log_str(*args,end=None):
    for i in args:
        print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"),i),end=end)