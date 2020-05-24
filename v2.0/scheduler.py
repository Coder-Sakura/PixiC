# coding=utf8
import time
# 多进程
from multiprocessing import Process

from crawler import Crawler
from bookmark import Bookmark
from api import app,db
from login import client
from config import *

class Scheduler(object):
	def scheduler_crawler(self,limit=USERS_CYCLE):
		"""
		关注画师作品
		"""
		c = Crawler()
		while True:
			c.run()
			time.sleep(USERS_CYCLE)
		
	def scheduler_api(self):
		"""
		api
		"""
		# db.create_db(thread_num=API_THREAD)
		app.run(API_HOST,API_PORT)

	def scheduler_bookmark(self,limit=BOOKMARK_CYCLE):
		"""
		收藏作品
		"""
		b = Bookmark()
		while True:
			b.run()
			time.sleep(BOOKMARK_CYCLE)

	def scheduler_ranking_list(self):
		"""
		每日榜单,暂不考虑
		"""
		pass

	def run(self):
		# client更新cookie
		client.check()

		if PIXIV_CRAWLER_ENABLED:
			pixiv_crawler = Process(target=self.scheduler_crawler)
			pixiv_crawler.start()

		if PIXIV_BOOKMARK_ENABLED:
			pixiv_bookmark = Process(target=self.scheduler_bookmark)
			pixiv_bookmark.start()

		if PIXIV_API_ENABLED:
			pixiv_api = Process(target=self.scheduler_api)
			pixiv_api.start()


if __name__ == '__main__':
	s = Scheduler()
	s.run()