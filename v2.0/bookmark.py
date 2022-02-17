# coding=utf8
"""
用户收藏爬虫
time: 2020-05-11
author: coder_sakura
"""
# import math
import json
import time

from downer import Downloader
from log_record import logger
from message import TEMP_MSG
from thread_pool import ThreadPool,callback
# TODO
from tag import TAG_FLAG_BOOKMARK


class Bookmark(object):
	def __init__(self):
		self.Downloader = Downloader()
		self.user_id = self.Downloader.client.user_id
		self.base_request = self.Downloader.baseRequest
		
		self.bookmark_url = "https://www.pixiv.net/ajax/user/{}/illusts/bookmarks".format(self.user_id)
		self.db = self.Downloader.db
		self.bookmark_page_offset = 48
		self.class_name = self.__class__.__name__
		# 2020/10/20 收藏更新机制
		# 默认第一次全更新
		self.day_count = 5
		self.day_all_update_num = 5
		self.day_limit = 800

	def get_page_bookmark(self, offset):
		"""
		根据offset和limit获取收藏插画的pid
		:params offset: 偏移量
		:return :对应offset和limit的pid列表,int类型
		"""
		params = {
			"tag":"",
			"offset":offset,
			"limit":self.bookmark_page_offset,
			"rest":"show",			
		}
		try:
			r = json.loads(self.base_request({"url":self.bookmark_url},params=params).text)
		except Exception as e:
			# 网络请求出错
			logger.warning(TEMP_MSG["BOOKMARK_PAGE_ERROR_INFO"].format(self.class_name,offset,offset+self.bookmark_page_offset))
			return None
		else:
			# 未登录
			if r["message"] == TEMP_MSG["UNLOGIN_TEXT"]:
				return TEMP_MSG["UL_TEXT"]

			res = r["body"]["works"]
			illusts_pid = [int(i["id"]) for i in res]
			return illusts_pid

	def check_update(self):
		"""
		检查是否更新,获取收藏第一页前十个插画的id
		更新机制:
			获取最新收藏的10条插画id,与数据库中的记录进行比对
			若最新收藏的10条插画id有一条在数据库中,则跳过;若不在则更新
			实际上是以最快10分钟内收藏10条新作品这个标准作为界限
		"""

		# 数据库开关若关闭,直接更新
		if hasattr(self.db,"pool") == False:
			logger.warning(TEMP_MSG["UPDATE_INFO"].format(self.class_name))
			return True

		res = self.get_page_bookmark(0)

		if res == TEMP_MSG["UL_TEXT"]:
			logger.warning(TEMP_MSG["UPDATE_CHECK_ERROR_INFO"].format(self.class_name))
			return False

		if res == None:
			logger.warning(TEMP_MSG["UPDATE_CHECK_ERROR_INFO"].format(self.class_name))
			return False
			
		# res类型不等于列表
		if type(res) != type([]):
			logger.warning(TEMP_MSG["UPDATE_CHECK_ERROR_INFO"].format(self.class_name))
			return False

		# 验证前十张
		for pid in res[:10]:
			if self.db.check_illust(pid,table="bookmark")[0] == False:
				logger.success(TEMP_MSG["UPDATE_INFO"].format(self.class_name))
				return True
		else:
			logger.warning(TEMP_MSG["UPDATE_CANLE_INFO"].format(self.class_name))
			return False

	def thread_by_illust(self, *args):
		"""
		线程任务函数
		"""
		pid = args[0]
		try:
			info = self.Downloader.get_illust_info(pid,extra="bookmark")
		except Exception as e:
			logger.warning(TEMP_MSG["ILLUST_NETWORK_ERROR_INFO"].format(self.class_name,pid,e))
			return 

		if info == None:
			logger.warning(TEMP_MSG["ILLUST_EMPTY_INFO"].format(self.class_name,pid))
			return

		# 数据库开关关闭
		if hasattr(self.db,"pool") == False:
			return 

		try:
			isExists,path = self.db.check_illust(pid,table="bookmark")
			# 数据库无该记录
			if isExists == False:
				# 第一次更新,pid不存在/被删除/无法找到
				if info == TEMP_MSG["PID_DELETED_TEXT"] or info == TEMP_MSG["PID_ERROR_TEXT"]:
					return 
					
				res = self.db.insert_illust(info,table="bookmark")
				if res:
					logger.success(TEMP_MSG["INSERT_SUCCESS_INFO"].format(self.class_name,pid))
				else:
					logger.warning(TEMP_MSG["INSERT_FAIL_INFO"].format(self.class_name,pid))
			# 数据库有该记录
			else:
				# pid不存在/被删除
				if info == TEMP_MSG["PID_DELETED_TEXT"]:
					result = self.db.delete_user_illust(key="pid",value=pid,table="bookmark")
					# 删除成功
					if result:
						logger.success(TEMP_MSG["DELELE_ILLUST_SUCCESS_INFO"].format(self.class_name,pid))
					else:
						logger.warning(TEMP_MSG["DELELE_ILLUST_FAIL_INFO"].format(self.class_name,pid))
				else:
					self.db.update_illust(info,table="bookmark")
		except Exception as e:
			logger.warning("thread_by_illust|Exception {}".format(e))

	def run(self):
		# TDOD TAG COUNT开始工作
		TAG_FLAG_BOOKMARK = False
		logger.info(TEMP_MSG["BEGIN_INFO"].format(self.class_name))
		# 更新机制判定
		if self.check_update() == False:
			logger.info(TEMP_MSG["SLEEP_INFO"].format(self.class_name))
			return

		try:
			offset = 0
			pool = ThreadPool(8)
			while True:
				# 累计更新小于5次,更新前800张,最多848张
				if self.day_count < self.day_all_update_num:
					if offset > self.day_limit:
						logger.info(TEMP_MSG["UPDATE_DAY_LIMIT_INFO"].format(self.class_name,self.day_limit,self.day_count))
						break

				pid_list = self.get_page_bookmark(offset)
				# 获取异常返回None
				if pid_list == None:
					logger.warning(TEMP_MSG["BOOKMARK_PAGE_ERROR_INFO"].format(self.class_name,offset,offset+self.bookmark_page_offset))
					continue
				
				# 未登录
				if pid_list == TEMP_MSG["UL_TEXT"]:
					logger.warning(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
					break

				# 无收藏返回[]
				if pid_list == []:
					break

				logger.info(TEMP_MSG["BOOKMARK_NOW_INFO"].format(self.class_name,offset,offset+self.bookmark_page_offset,len(pid_list)))
				for pid in pid_list:
					pool.put(self.thread_by_illust,(pid,),callback)

				offset += self.bookmark_page_offset

				time.sleep(1)
		except Exception as e:
			logger.warning("Exception {}".format(e))
		finally:
			# 累计等于5次,不触发更新限制机制,全更新完后恢复day_count
			if self.day_count == self.day_all_update_num:
				logger.success(TEMP_MSG["UPDATE_DAY_ALL_INFO"].format(self.class_name))
				self.day_count = 0
			else:
				self.day_count += 1

			pool.close()
			# TDOD TAG COUNT完成工作
			TAG_FLAG_BOOKMARK = True
		logger.info(TEMP_MSG["SLEEP_INFO"].format(self.class_name))
		logger.info("="*48)


# if __name__ == '__main__':
# 	from config import BOOKMARK_CYCLE
# 	b = Bookmark()
# 	while True:
# 		b.run()
# 		time.sleep(BOOKMARK_CYCLE)