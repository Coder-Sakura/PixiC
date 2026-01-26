# coding=utf8
import time
from multiprocessing import Process
import multiprocessing

from config import API_HOST,API_PORT,BOOKMARK_CYCLE,DB_ENABLE,USERS_CYCLE,\
	PIXIV_BOOKMARK_ENABLED,PIXIV_CRAWLER_ENABLED,PIXIV_API_ENABLED
from login import client
from log_record import logger
from message import TEMP_MSG


class Scheduler(object):
	def __init__(self):
		# 用于存储运行中的子进程对象，格式为 {进程名: Process对象}
		self.processes = {}
		# 进程间通信的停止事件，用于通知所有子进程统一停止
		self._stop_event = multiprocessing.Event()

	def scheduler_crawler(self,limit=USERS_CYCLE):
		# 关注画师作品循环
		from crawler import Crawler
		c = Crawler()
		while not self._stop_event.is_set():
			c.run()
			time.sleep(USERS_CYCLE)
		
	def scheduler_api(self):
		# API 服务
		from api import app
		try:
			try:
				api_port = int(API_PORT)
			except Exception:
				api_port = API_PORT
			app.run(API_HOST, api_port)
		except Exception as e:
			logger.warning(f"API run error: {e}")

	def scheduler_bookmark(self, limit=BOOKMARK_CYCLE):
		# 收藏作品循环
		from bookmark import Bookmark
		b = Bookmark()
		while not self._stop_event.is_set():
			b.run()
			time.sleep(BOOKMARK_CYCLE)

	def _start_process(self, name, target):
		"""启动子进程并记录其 PID"""
		p = Process(target=target, name=name)
		p.start()
		self.processes[name] = p
		logger.info(f"Process started: {name} (pid={p.pid})")

	def _terminate_all(self):
		"""终止所有已记录的子进程"""
		for name,p in list(self.processes.items()):
			try:
				if p.is_alive():
					p.terminate()
					p.join(timeout=5)
					logger.info(f"Process terminated: {name}")
			except Exception as e:
				logger.warning(f"Terminate {name} error: {e}")
		self.processes.clear()

	def stop(self):
		"""触发停止事件并清理进程"""
		self._stop_event.set()
		self._terminate_all()

	def run(self):
		"""主调度循环"""
		logger.success(TEMP_MSG["VERSION_INFO"])
		# client更新cookie
		try:
			client.check()
		except Exception as e:
			logger.warning(f"Client check error: {e}")

		# 根据开关启动对应子进程
		if PIXIV_CRAWLER_ENABLED:
			self._start_process("crawler", self.scheduler_crawler)

		if PIXIV_BOOKMARK_ENABLED:
			self._start_process("bookmark", self.scheduler_bookmark)

		if PIXIV_API_ENABLED and DB_ENABLE:
			self._start_process("api", self.scheduler_api)

		try:
			# 监控子进程状态，若任一进程异常退出则触发全局停止
			while not self._stop_event.is_set():
				for name,p in list(self.processes.items()):
					if not p.is_alive():
						logger.warning(f"Process died: {name} (exitcode={p.exitcode})")
						self._stop_event.set()
						break
				if self._stop_event.is_set():
					break
				time.sleep(1)
		finally:
			self._terminate_all()


if __name__ == '__main__':
	s = Scheduler()
	s.run()
