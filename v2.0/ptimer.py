# coding=utf8
"""
通过智能等待处理限制访问
time: 2023-03-16
author: coder_sakura
"""

import time
import random
import threading

from message import TEMP_MSG
from log_record import logger


def random_cycle_time():
    return 20
    # return random.choice([30,40,50])


class Timer:
    """
    触发限制后周期性主动轮询
    或超过_limit_time后主动退出,进而恢复原先的任务
    """
    def __init__(self):
        # 每轮等待时间
        self.poll_cycle_time = random_cycle_time
        # 记录已等待时间
        self._time = 0
        # 官方限制时间-粗略估算
        self._limit_time = 180
        self._limit_time = 120
        self.Downloader = None
        self.pid = None
        self.extra = None

    def waiting(self,resp:str or dict):
        """
        return: 
            resp: pid info
            func: 继续周期性轮询
        """
        # logger.debug(f"waiting:resp - {resp}")
        if type(resp) == type("") and not resp == TEMP_MSG["LIMIT_TEXT"]:
            return 
            

        # 请求正常--退出
        if type(resp) == type({}) and not resp.get("error"):
            logger.success(f"waiting:resp - {resp}")
            return resp
        # 触发限制
        elif resp == TEMP_MSG["LIMIT_TEXT"]:
            self._time += self.poll_cycle_time()
            time.sleep(self.poll_cycle_time())
            logger.debug(f"线程ID:{threading.get_ident()}:已休眠{self._time}/{self._limit_time}秒,尝试重新访问<{self.pid}>")
            # return self.waiting(random.choice(
            #     [
            #         TEMP_MSG["LIMIT_TEXT"],
            #         self.Downloader.get_illust_info(self.pid,extra="bookmark")
            #     ]
            #     )
            # )
            return self.waiting(self.Downloader.get_illust_info\
                (self.pid,extra=self.extra))
        # 已等待时间>=官方限制时间--退出
        elif self._time >= self._limit_time:
            logger.debug(f"线程ID:{threading.get_ident()}:已休眠{self._time}/{self._limit_time}秒,尝试重新访问<{self.pid}>-")
            return self.waiting(self.Downloader.get_illust_info\
                (self.pid,extra=self.extra))
        else:
            self._time += self.poll_cycle_time()
            time.sleep(self.poll_cycle_time())
            logger.debug(f"线程ID:{threading.get_ident()}:已休眠{self._time}/{self._limit_time}秒,尝试重新访问<{self.pid}>--")
            return self.waiting(self.Downloader.get_illust_info\
                (self.pid,extra=self.extra))