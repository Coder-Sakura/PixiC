# coding=utf8
"""
用户收藏爬虫
time: 2020-05-11
author: coder_sakura
"""
import time
import json
import queue
import threading
import math
from lxml import etree

from downer import Downloader
from logstr import log_str
from test_threading_list import *

class Bookmark(object):
	def __init__(self):
		self.bookmark = 'https://www.pixiv.net/bookmark.php'
		self.base_request = Downloader.baseRequest

		self.db = Downloader.db
		self.db.create_db()
		self.selectMaxXpath = """//span[@class="count-badge"]/text()"""
		self.selectPidXpath = """//li[contains(@class,"image-item")]//img/following-sibling::div[1]/@data-id"""

	def get_total_page(self):
		"""
		获取最大页数进行处理,向上取整
		9/4=3
		:return :最大页数
		"""
		obj = etree.HTML(self.base_request(options={"url":self.bookmark}).text)
		n = obj.xpath(self.selectMaxXpath)[0][:-1]
		log_str("共收藏{}张插画".format(n))
		return math.ceil(int(n)/20)

	def get_html(self,p):
		"""
		:params p: 页数
		:return : 第p页收藏的源码
		"""
		return self.base_request(options={"url":self.bookmark},params={"p":int(p)}).text

	def get_pid(self,obj):
		"""
		获取obj对象中的pid,一页20个,将获取的pid转为int类型
		当小于20个时,一般是作品被删除,其次才是网站结构发生改变
		:return : pid列表
		"""
		return [int(i) for i in obj.xpath(self.selectPidXpath)]

	def check_update(self):
		"""
		检查是否更新,获取收藏第一页前十个插画的id
		更新机制:
			获取最新收藏的10条插画id,与数据库中的记录进行比对
			若最新收藏的10条插画id有一条在数据库中,则跳过;若不在则更新
			本意上是以最快10分钟内收藏10条新作品这个标准作为界限
		"""
		a = self.get_pid(etree.HTML(self.get_html(1)))[:10]
		for i in a:
			if self.db.check_illust(i,table="bookmark")[0] == False:
				log_str("{} 进行更新".format(__file__.split("\\")[-1].split(".")[0]))
				return True
		else:
			log_str("{} 暂不更新".format(__file__.split("\\")[-1].split(".")[0]))
			return False

	def thread_by_illust(self,*args):
		pid = args[0]
		isExists,path = self.db.check_illust(pid,table="bookmark")

		if path == None:
			# 会根据每次请求的收藏数来进行判断是否下载
			try:
				info = Downloader.get_illust_info(pid,extra="bookmark")
			except Exception as e:
				log_str("{}请求错误:{}".format(pid,e))
				return 

			if info == None:
				log_str("该作品{}已被删除,或作品ID不存在.".format(pid))
				return

			if isExists == False:
				# 数据库无该记录
				res = self.db.insert_illust(info,table="bookmark")
				if res == False:
					log_str("插入{}失败".format(pid))
				else:
					log_str("插入{}成功".format(pid))

	def run(self):
		log_str("{} 开始轮询,获取收藏列表".format(self.__class__.__name__))
		# 更新机制判定
		if self.check_update() == False:
			log_str("{} 进入休眠".format(self.__class__.__name__))
			return

		try:
			max_num = self.get_total_page()
			pool = ThreadPool(8)

			for i in range(1,max_num+1):
				log_str("当前收藏页: 第{}页".format(i))
				pid_list = self.get_pid(etree.HTML(self.get_html(i)))

				for pid in pid_list:
					pool.put(self.thread_by_illust,(pid,),callback)

				time.sleep(3)
		except Exception as e:
			log_str("Exception",e)
		finally:
			pool.close()
		log_str("{} 进入休眠".format(self.__class__.__name__))


# if __name__ == '__main__':
# 	from config import BOOKMARK_CYCLE
# 	b = Bookmark()
# 	while True:
# 		b.run()
# 		time.sleep(BOOKMARK_CYCLE)