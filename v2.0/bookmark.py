# coding=utf8
"""
用户收藏爬虫
time: 2020-05-11
author: coder_sakura
"""
import time
import json
import math
from lxml import etree

from downer import Downloader
from logstr import log_str
from thread_pool import *

class Bookmark(object):
	def __init__(self):
		self.user_id = Downloader.client.user_id
		self.base_request = Downloader.baseRequest
		
		self.bookmark_url = "https://www.pixiv.net/ajax/user/{}/illusts/bookmarks".format(self.user_id)
		self.db = Downloader.db

	def get_page_bookmark(self,offset):
		"""
		根据offset和limit获取收藏插画的pid
		:params offset: 偏移量
		:return :对应offset和limit的pid列表,int类型
		"""
		params = {
			"tag":"",
			"offset":offset,
			"limit":100,
			"rest":"show",			
		}
		try:
			r = json.loads(self.base_request({"url":self.bookmark_url},params=params).text)
			res = r["body"]["works"]
			total = r["body"]["total"]
			illusts_pid = [int(i["illustId"]) for i in res]
		except Exception as e:
			log_str("bookmark获取收藏出错: 第{}-{}张失败".format(offset,offset+100))
			return None,None
		else:
			return illusts_pid,total

	def check_update(self):
		"""
		检查是否更新,获取收藏第一页前十个插画的id
		更新机制:
			获取最新收藏的10条插画id,与数据库中的记录进行比对
			若最新收藏的10条插画id有一条在数据库中,则跳过;若不在则更新
			本意上是以最快10分钟内收藏10条新作品这个标准作为界限
		"""
		res = self.get_page_bookmark(0)
		if res[0] == None:
			return False
		else:
			# total = res[1]
			# if 
			# 验证前十张
			for i in res[:10]:
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
			else:
				# 更新记录
				self.db.updata_illust(info)

	def run(self):
		log_str("{} 开始轮询,获取收藏列表".format(self.__class__.__name__))
		# 更新机制判定
		# if self.check_update() == False:
		# 	log_str("{} 进入休眠".format(self.__class__.__name__))
		# 	return

		try:
			offset = 0
			pool = ThreadPool(8)

			while True:
				pid_list = self.get_page_bookmark(offset)[0]
				# 获取异常返回None
				if pid_list == None:
					continue
				
				# 无收藏返回[]
				if pid_list == []:
					break

				log_str("当前收藏: 第{}-{}张获取成功,共{}张可用".format(offset,offset+100,len(pid_list)))
				for pid in pid_list:
					pool.put(self.thread_by_illust,(pid,),callback)

				offset += 100

				time.sleep(1)
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