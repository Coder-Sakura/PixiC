# -*- encoding: utf-8 -*-
'''
@File    :   tag.py
@Time    :   2022/02/07 16:16:37
@Author  :   Coder-Sakura
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import collections
import time
from typing import List

from downer import Downloader
from log_record import logger
# from message import 


TAG_FLAG_USER = True
TAG_FLAG_BOOKMARK = True


class TagTask:
    def get_tag_count(self,tag_group:list)->list:
        return collections.Counter(tag_group)


    def main(self,quicky=False):
        if not quicky:
            time.sleep(60)

        if TAG_FLAG_BOOKMARK and TAG_FLAG_USER:
            pass

"""
db.random_illust,获取到所有pid
db,select_illust,获取对应pid信息
split_tag,获取tag
===
def split_tag(info):
    new_list = []
    for _ in info["tag"].split("、"):
        if "/" in _:
            new_list.extend(_.split("/"))
        else:
            new_list.extend([_])
    return new_list

===
每20个tag组汇总后,进行计数,然后逐一
collections.Count,获取new_list计数情况

mini_result = result[1:21]
all_list = []
for pid in mini_result:
    info = db.select_illust(pid["pid"], table="bookmark")
    split_list = info[0]["tag"].split("、")
    new_list = get_tag(split_list)
    all_list.extend(new_list)

import collections
c = collections.Counter(all_list)
"""