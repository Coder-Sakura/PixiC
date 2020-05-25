# coding=utf8
"""
关注画师爬虫
time: 2020-05-11
author: coder_sakura
"""
import time
import json

from downer import Downloader
from logstr import log_str
from thread_pool import *


class Crawler(object):
	def __init__(self):
		self.user_id = Downloader.client.user_id
		self.base_request = Downloader.baseRequest

		# # 作品数据
		# self.ajax_illust = "https://www.pixiv.net/ajax/illust/{}"
		# 画师列表
		self.follw_url = "https://www.pixiv.net/ajax/user/{}/following".format(self.user_id)
		# 作品链接,存数据库
		self.artworks_url = "https://www.pixiv.net/artworks/{}"
		# 画师作品列表
		self.all_illust_url = "https://www.pixiv.net/ajax/user/{}/profile/all"
		self.file_manager = Downloader.file_manager
		self.db = Downloader.db

	def get_page_users(self,offset):
		"""
		:params offset 偏移量,按照偏移量获得limit范围内的画师
		:return 接口数据中的画师数组
		"""
		params = {
			"offset":offset,
			"limit":100,
			"rest":"show",			
		}
		return json.loads(self.base_request({"url":self.follw_url},params=params).text)['body']['users']

	def get_users(self):
		"""
		:return: 所有关注画师的uid,userName,latest_id(最新的pid)
		:[{"uid":uid,"userName":userName,"latest_id":latest_id},...]
		"""
		offset = 0
		users_info_list = []

		while True:
			u_list = self.get_page_users(offset)

			for u in u_list:
				user_info = {}
				user_info["uid"] = int(u["userId"])
				user_info["userName"] = u["userName"]

				if u["illusts"] == []:
					user_info["latest_id"] = -1
					log_str("{}无作品...".format(u["userId"]))
					# 无作品不做动作
					continue
				else:
					user_info["latest_id"] = int(u["illusts"][0]["illustId"])

				users_info_list.append(user_info)

			if len(u_list) != 100:
				break

			offset += 100

		return users_info_list
		# print(users_info_list)

	def get_user_illust(self,u):
		"""
		:params u: 画师信息,字段包括:uid,userName,latest_id
		:return user_illust_list: 画师信息包括:uid,userName,latest_id,path
		"""
		u["path"] = self.file_manager.mkdir_painter(u)
		illust_url = self.all_illust_url.format(u["uid"])
		try:
			u_json = json.loads(self.base_request({"url":illust_url}).text)["body"]
			i = u_json["illusts"]
			m = u_json["manga"]
			# 列表推导式合并取keys,转为list
			user_illust_list = list([dict(i) if len(m) == 0 else dict(i,**m)][0].keys())
		except Exception as e:
			log_str("crwaler:获取画师数据出错 {}".format(e))
			return []
		else:
			return user_illust_list

	def thread_by_illust(self,*args):
		pid = args[0]
		isExists,path = self.db.check_illust(pid)
		# print(isExists,path)

		"""
		if isExists == False and path == None:
			# 数据库没有记录也没有下载,
			# 正常流程 
			pass

		if isExists == True and path == None:
			# 数据库有记录但没有下载,
			# 验证收藏数并下载
			pass

		if isExists == True and path != None:
			# 数据库有记录,也有下载,ok的
			# config设置一个参数,控制每个轮询是否更新已有作品数据
			pass

		if isExists == False and path != None:
			# 下载了,但数据库有记录
			# 不可能发生,下载了有path,也得insert才有数据,不然查询到的path应该是None
			pass
		"""

		if path == None:
			# 会根据每次请求的收藏数来进行判断是否下载
			try:
				info = Downloader.get_illust_info(pid)
			except Exception as e:
				log_str("{}请求错误:{}".format(pid,e))
				return 

			if info == None:
				log_str("该作品{}已被删除,或作品ID不存在.".format(pid))
				return

			# 数据库无该记录
			if isExists == False:
				res = self.db.insert_illust(info)
				if res == False:
					log_str("插入{}失败".format(pid))
				else:
					log_str("插入{}成功".format(pid))
			# 数据库有该记录
			else:
				# 更新记录
				self.db.updata_illust(info)

	def run(self):
		log_str("{} 开始轮询,获取关注列表...".format(self.__class__.__name__))
		try:
			u_list = self.get_users()
		except Exception as e:
			log_str("{} 获取关注列表出错".format(__file__.split("\\")[-1].split(".")[0]))
			log_str("{} 进入休眠".format(__file__.split("\\")[-1].split(".")[0]))
		log_str("{} 成功获取关注列表.共{}位关注用户".format(self.__class__.__name__,len(u_list)))

		try:
			pool = ThreadPool(8)
			for u in u_list:
				all_illust = self.get_user_illust(u)
				latest_id = self.db.check_user(u)
				d_total = self.db.get_total(u)
				# log_str("{}|{} {} {} {}".format(u["uid"],u["latest_id"],latest_id,d_total,total))
				log_str("当前画师: {}(pid:{}) |作品数: {}".format(u["userName"],u["uid"],len(all_illust)))
				if u["latest_id"] >= latest_id and d_total < len(all_illust):
					# 满足条件更新
					log_str("更新{}|{} {} {} {}".format(u["uid"],u["latest_id"],latest_id,d_total,total))
					self.db.update_latest_id(u)

					for pid in all_illust:
						pool.put(self.thread_by_illust,(pid,),callback)

					time.sleep(3)
					# self.threa_scheduler(u,all_illust)
				else:
					# print("不更新")
					continue

			pool.close()
		except Exception as e:
			log_str("Exception",e)
		finally:
			pool.close()
		log_str("{} 进入休眠".format(__file__.split("\\")[-1].split(".")[0]))


# if __name__ == '__main__':
# 	from config import USERS_CYCLE
# 	c = Crawler()
# 	while True:
# 		c.run()
# 		time.sleep(USERS_CYCLE)