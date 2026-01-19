# coding=utf8
import time
import random
from multiprocessing import Process

from config import API_HOST,API_PORT,BOOKMARK_CYCLE,DB_ENABLE,USERS_CYCLE,\
	PIXIV_BOOKMARK_ENABLED,PIXIV_CRAWLER_ENABLED,PIXIV_API_ENABLED
from login import client
from log_record import logger
from message import TEMP_MSG


class Scheduler(object):
	def scheduler_crawler(self,limit=USERS_CYCLE):
		"""
		关注画师作品
		"""
		from crawler import Crawler
		c = Crawler()
		while True:
			try:
				c.run()
				time.sleep(USERS_CYCLE)
			except KeyboardInterrupt as e:
				break
		
	def scheduler_api(self):
		"""
		API
		"""
		from api import app
		app.run(API_HOST,API_PORT)

	def scheduler_bookmark(self, limit=BOOKMARK_CYCLE):
		"""
		收藏作品
		"""
		from bookmark import Bookmark
		b = Bookmark()
		while True:
			try:
				b.run()
				time.sleep(BOOKMARK_CYCLE)
			except KeyboardInterrupt as e:
				break

	def run(self):
		logger.success(TEMP_MSG["VERSION_INFO"])
		# client更新cookie
		client.check()

		if PIXIV_CRAWLER_ENABLED:
			time.sleep(round(random.uniform(1.0, 3.0), 2))
			pixiv_crawler = Process(target=self.scheduler_crawler)
			pixiv_crawler.start()

		if PIXIV_BOOKMARK_ENABLED:
			time.sleep(round(random.uniform(1.0, 3.0), 2))
			pixiv_bookmark = Process(target=self.scheduler_bookmark)
			pixiv_bookmark.start()

		if PIXIV_API_ENABLED and DB_ENABLE:
			pixiv_api = Process(target=self.scheduler_api)
			pixiv_api.start()


if __name__ == '__main__':
	s = Scheduler()
	s.run()