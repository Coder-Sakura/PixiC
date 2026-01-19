# coding=utf8
"""
用户收藏爬虫
time: 2020-05-11
author: coder_sakura
"""
# import math
import json
import time

from config import BOOKMARK_HIDE_ENABLE,SKIP_EXISTS_ILLUST,\
	BOOKMARK_PATH,SLOW_MODE,THREAD_NUM,LOOP_LIMIT,BOOKMARK_CYCLE
from downer import Downloader
from log_record import logger
from message import TEMP_MSG
from thread_pool import ThreadPool,callback

THREAD_NUM = 4 if not SLOW_MODE else 1


class Bookmark(object):
	def __init__(self):
		self.Downloader = Downloader()
		self.user_id = self.Downloader.client.user_id
		self.base_request = self.Downloader.baseRequest
		
		self.bookmark_url = "https://www.pixiv.net/ajax/user/{}/illusts/bookmarks".format(self.user_id)
		self.rest_list = ["show", "hide"] if BOOKMARK_HIDE_ENABLE else ["show"]
		self.rest_dict = {"show": "公开", "hide": "未公开"}
		
		self.db = self.Downloader.db
		self.file_manager = self.Downloader.file_manager
		self.bookmark_page_offset = 48
		self.class_name = self.__class__.__name__

		# 2020/10/20 收藏更新机制
		# 默认第一次全更新
		# self.day_count = 5
		# self.day_all_update_num = 5
		self.illustCount = 0			# 作品抓取计数器

	def get_page_bookmark(self, offset, rest="show", raw=False):
		"""
		根据offset和limit获取收藏插画的pid
		:params offset: 偏移量
		:params rest: 公开/未公开收藏
		:params raw: 是否返回原始数据
		:return :对应offset和limit的pid列表,int类型
		"""
		params = {
			"tag": "",
			"offset": offset,
			"limit": self.bookmark_page_offset,
			"rest": rest,
		}
		try:
			r = json.loads(self.base_request({"url":self.bookmark_url},params=params).text)
		except Exception as e:
			# 网络请求出错
			logger.warning(TEMP_MSG["BOOKMARK_PAGE_ERROR_INFO"].format(self.class_name,offset,offset+self.bookmark_page_offset))
			return None
		else:
			if raw:
				return r
			else:
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
			logger.warning(TEMP_MSG["UPDATE_INFO"])
			return True

		# 判断非公开及公开
		res = self.get_page_bookmark(offset=0, raw=True)
		if BOOKMARK_HIDE_ENABLE:
			res_hide = self.get_page_bookmark(offset=0, rest="hide", raw=True)

		# 未登录
		if res == TEMP_MSG["UL_TEXT"]:
			logger.warning(TEMP_MSG["UPDATE_CHECK_ERROR_INFO"].format(self.class_name))
			return False

		# 公开收藏 - 错误
		if res["error"]:
			logger.warning(TEMP_MSG["UPDATE_CHECK_ERROR_INFO"].format(self.class_name))
			logger.warning(f"<res> - {res}")
			return False

		# 验证前十张
		for _ in res["body"]["works"][:10]:
			if not self.db.check_illust(int(_["id"]),table="bookmark")[0]:
				logger.success(TEMP_MSG["UPDATE_INFO2"].format(self.class_name))
				return True
		
		if BOOKMARK_HIDE_ENABLE:
			# 未公开收藏 - 错误/无权限
			if res_hide["error"]:
				if TEMP_MSG["NO_AUTH"] in res_hide["message"]:
					logger.warning(TEMP_MSG["UPDATE_CHECK_NO_AUTH_INFO"].format(
						self.class_name, self.user_id, self.user_id))
				else:
					logger.warning(TEMP_MSG["UPDATE_CHECK_ERROR_INFO"].format(self.class_name))
				logger.warning(f"<res_hide> - {res_hide}")
				return False
			# 作品为空
			if not res["body"]["works"] and not res_hide["body"]["works"]:
				logger.warning(TEMP_MSG["UPDATE_CHECK_EMPTY_INFO"].format(self.class_name))
				return False
			# 验证前十张
			for _ in res_hide["body"]["works"][:10]:
				if not self.db.check_illust(int(_["id"]),table="bookmark")[0]:
					logger.success(TEMP_MSG["UPDATE_INFO2"].format(self.class_name))
					return True
		
		logger.warning(TEMP_MSG["UPDATE_CANLE_INFO"].format(self.class_name))
		return False

	def thread_by_illust(self, *args):
		"""
		线程任务函数
		"""
		pid = args[0]
		info = None

		# 跳过已下载插画的请求
		if SKIP_EXISTS_ILLUST:
			# 先检查文件夹,再检查数据库
			if self.file_manager.search_isExistsPid(BOOKMARK_PATH,"b",*(pid,)):
				logger.debug(f"SKIP_EXISTS_ILLUST FM - {pid}")
				return info
			# TODO check_illust返回的值用变量接收,避免多次调用check_illust函数
			elif hasattr(self.db,"pool") and self.db.check_illust(pid,table="bookmark")[0]:
				logger.debug(f"SKIP_EXISTS_ILLUST DB - {pid}")
				return info
		
		try:
			info = self.Downloader.get_illust_info(pid,extra="bookmark")
			self.illustCount += 1
			logger.debug(f"{self.illustCount}")
		except Exception as e:
			logger.warning(TEMP_MSG["ILLUST_NETWORK_ERROR_INFO"].format(self.class_name,pid,e))
			logger.warning(f"{pid} INFO:{info}")
			return info			

		if not info: 
			logger.warning(TEMP_MSG["ILLUST_EMPTY_INFO"].format(self.class_name,pid))
			return info

		# 数据库开关关闭
		if hasattr(self.db,"pool") == False:
			return info

		try:
			isExists,path = self.db.check_illust(pid,table="bookmark")
			# 数据库无该记录
			if isExists == False:
				# 第一次更新,pid不存在/被删除/无法找到
				if info == TEMP_MSG["PID_DELETED_TEXT"] or info == TEMP_MSG["PID_ERROR_TEXT"]:
					return info
					
				res = self.db.insert_illust(info,table="bookmark")
				if res:
					logger.success(TEMP_MSG["INSERT_SUCCESS_INFO"].format(self.class_name,pid))
				else:
					logger.warning(TEMP_MSG["INSERT_FAIL_INFO"].format(self.class_name,pid))
			# 数据库有该记录
			else:
				# pid不存在/已删除/已设为私密/无权限访问
				if info == TEMP_MSG["PID_DELETED_TEXT"] or\
					info == TEMP_MSG["PID_UNAUTH_ACCESS"] or\
					info == TEMP_MSG["PID_UNAUTH_ACCESS_2"]:
					result = self.db.delete_user_illust(key="pid",value=pid,table="bookmark")
					# 删除成功
					if result:
						logger.success(TEMP_MSG["DELELE_ILLUST_SUCCESS_INFO"].format(self.class_name,pid))
					else:
						logger.warning(TEMP_MSG["DELELE_ILLUST_FAIL_INFO"].format(self.class_name,pid))
				else:
					result = self.db.update_illust(info,table="bookmark")
					if result:logger.success(TEMP_MSG["UPDATE_SUCCESS_INFO"].format(self.class_name,pid))
		except Exception as e:
			logger.warning("thread_by_illust|Exception {}".format(e))
			logger.warning(f"{pid} INFO:{info}")

	@logger.catch
	def run(self):
		logger.info(TEMP_MSG["BEGIN_INFO"].format(self.class_name))
		# 更新机制判定
		if self.check_update() == False:
			logger.info(TEMP_MSG["SLEEP_INFO"].format(self.class_name))
			return

		try:
			offset = 0
			self.illustCount = 0
			pool = ThreadPool(THREAD_NUM)
			# 分别获取公开/非公开收藏插画
			for rest in self.rest_list:
				logger.info(f"===== 开始获取{self.rest_dict[rest]}收藏 =====")
				while True:
					raw_data = self.get_page_bookmark(offset, rest, raw=True)
					if not self.check_page_bookmarkData(offset, raw_data):
						offset = 0
						break

					# 去除已删除的插画
					# pid_list = [int(i["id"]) for i in raw_data["body"]["works"] if i["title"] != "-----" and i["userId"] != 0]
					pid_list = []
					for i in raw_data["body"]["works"]:
						if i["title"] != "-----" and i["userId"] != 0:
							pid_list.append(int(i["id"]))
						else:
							logger.warning(f'{TEMP_MSG["PID_DELETED_TEXT"]} - {int(i["id"])}')

					logger.info(TEMP_MSG["BOOKMARK_NOW_INFO"].format(offset,offset+self.bookmark_page_offset,len(pid_list)))
					for pid in pid_list:
						if self.illustCount > LOOP_LIMIT and LOOP_LIMIT != 0:
							# 达到设置的单轮次抓取上限,进入休眠
							self.illustCount = 0
							logger.info(TEMP_MSG["LOOP_LIMIT_INFO"].format(BOOKMARK_CYCLE))
							time.sleep(BOOKMARK_CYCLE)

						# 每100张休眠60秒,只在慢速模式下生效
						if self.illustCount % 100 == 0 and SLOW_MODE\
							and self.illustCount != 0:
							logger.info(TEMP_MSG["SLOW_LIMIT_INFO"])
							time.sleep(60)

						# 线程池添加任务
						pool.put(self.thread_by_illust,(pid,),callback)
						# time.sleep(0.1)	# test

					offset += self.bookmark_page_offset
		except Exception as e:
			logger.warning("Exception {}".format(e))
			pool.terminate()  # 强制终止所有线程
		except KeyboardInterrupt as e:
			pool.terminate()
		else:
			pool.close()

		logger.info("="*48)
		logger.info(TEMP_MSG["SLEEP_INFO"].format(self.class_name))
	
	def check_page_bookmarkData(self, offset, raw_data):
		"""
		检查插画数据
		:return: 
			True	继续执行
			False	异常数据
		"""
		# logger.debug(f"{raw_data}")

		# 未登录
		if raw_data["message"] == TEMP_MSG["UNLOGIN_TEXT"]:
			logger.warning(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
			return False
		
		# 无收藏返回[]
		if raw_data["body"]["works"] == []:
			logger.warning(TEMP_MSG["BOOKMARK_PAGE_EMPTY_INFO"].format(self.class_name,
				offset, offset+self.bookmark_page_offset))
			return False
		
		# 获取异常返回None   TODO None处理
		if raw_data["body"]["works"] == None:
			logger.warning(TEMP_MSG["BOOKMARK_PAGE_ERROR_INFO"].format(
				self.class_name, offset, offset+self.bookmark_page_offset
			))
			return False

		# 正常情况
		return True
				
		# TODO 检查插画已删除的作品
		# pid_list,raw_data = Downloader.deleteIllustFlow(raw_data)
		# TODO 传入pid_list -->未使用
		# elif type(raw_data) == type(list()):
		# 	if raw_data == []:				# 无收藏返回[]
		# 		logger.warning(TEMP_MSG["BOOKMARK_PAGE_EMPTY_INFO"].format(self.class_name,
		# 			offset, offset+self.bookmark_page_offset))
		# 		return False


# if __name__ == '__main__':
# 	from config import BOOKMARK_CYCLE
# 	b = Bookmark()
# 	while True:
# 		b.run()
# 		time.sleep(BOOKMARK_CYCLE)