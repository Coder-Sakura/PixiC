# coding=utf8
"""
关注画师爬虫
time: 2020-05-11
author: coder_sakura
"""
import json
import time
import re

from downer import Down
from logstr import log_str
from message import TEMP_MSG
from thread_pool import ThreadPool,callback


class Crawler(object):
	def __init__(self):
		self.Downloader = Down()
		self.user_id = self.Downloader.client.user_id
		self.base_request = self.Downloader.baseRequest

		# 公开/非公开 见get_page_users
		self.rest_list = ["show","hide"]
		# 画师列表
		self.follw_url = "https://www.pixiv.net/ajax/user/{}/following".format(self.user_id)
		# 作品链接,存数据库
		self.artworks_url = "https://www.pixiv.net/artworks/{}"
		# 画师作品列表
		self.all_illust_url = "https://www.pixiv.net/ajax/user/{}/profile/all"
		self.file_manager = self.Downloader.file_manager
		self.db = self.Downloader.db
		self.class_name = self.__class__.__name__

	def get_page_users(self,offset,rest="show"):
		"""
		:params offset 偏移量,按照偏移量获得limit范围内的画师
		:return 接口数据中的画师数组
		"""
		params = {
			"offset":offset,
			"limit":100,
			"rest":rest,			
		}
		try:
			r = json.loads(self.base_request({"url":self.follw_url},params=params).text)
		except Exception as e:
			# 网络请求出错
			log_str(TEMP_MSG["FOLLOW_PAGE_ERROR_INFO"].format(self.class_name,offset,offset+100))
			log_str(e)
			return None
		else:
			# 未登录
			if r["message"] == TEMP_MSG["UNLOGIN_TEXT"]:
				log_str(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
				return TEMP_MSG["UL_TEXT"]
				
			res = r['body']['users']
			return res

	def get_users(self):
		"""
		:return: 所有关注画师的uid,userName,latest_id(最新的pid)
		:[{"uid":uid,"userName":userName,"latest_id":latest_id},...]
		"""
		offset = 0
		users_info_list = []
		err_count = 0
		err_limit = 10

		for rest in self.rest_list:
			while True:
				u_list = self.get_page_users(offset,rest=rest)

				# 网络请求出错
				if u_list == None:
					# 累计10次网络错误
					if err_count < err_limit:
						offset += 100
						err_count += 1
						continue
					else:
						break

				# 未登录
				if u_list == TEMP_MSG["UL_TEXT"]:
					users_info_list = TEMP_MSG["UL_TEXT"]
					break

				# 获取所有关注完毕
				if u_list == []:
					break

				for u in u_list:
					user_info = {}
					user_info["uid"] = int(u["userId"])
					# userName = re.sub('[\\\/:*?"<>|]','_',u["userName"])
					userName = re.sub(r'[\s\/:*?"<>|\\]','_',u["userName"])
					user_info["userName"] = userName

					if u["illusts"] == []:
						user_info["latest_id"] = -1
						log_str(TEMP_MSG["FOLLOW_NO_ILLUSTS_INFO"].format(self.class_name,u["userName"],u["userId"]))
						# 无作品不做动作
						# continue
					else:
						user_info["latest_id"] = int(u["illusts"][0]["id"])

					users_info_list.append(user_info)

				offset += 100

		return users_info_list

	def get_user_illust(self, u):
		"""
		:params u: 画师信息--字典
		:return user_illust_list: 画师信息包括:uid,userName,latest_id,path
		"""
		u["path"] = self.file_manager.mkdir_painter(u)
		illust_url = self.all_illust_url.format(u["uid"])
		try:
			u_json = json.loads(self.base_request({"url":illust_url}).text)["body"]
			i = u_json.get("illusts",[])
			m = u_json.get("manga",[])
			# 列表推导式合并取keys,转为list
			user_illust_list = list([dict(i) if len(m) == 0 else dict(i,**m)][0].keys())
		except Exception as e:
			log_str(TEMP_MSG["FOLLOW_DATA_ERROR_INFO"].format(self.class_name,e))
			return []
		else:
			return user_illust_list

	def thread_by_illust(self, *args):
		"""
		线程任务函数
		"""
		pid = args[0]
		try:
			info = self.Downloader.get_illust_info(pid)
		except Exception as e:
			log_str(TEMP_MSG["ILLUST_NETWORK_ERROR_INFO"].format(self.class_name,pid,e))
			return 

		if info == None:
			log_str(TEMP_MSG["ILLUST_EMPTY_INFO"].format(self.class_name,pid))
			return

		# 数据库开关关闭
		if hasattr(self.db,"pool") == False:
			return 

		try:
			isExists,path = self.db.check_illust(pid)
			# 数据库无该记录
			if isExists == False:
				# 第一次更新,pid不存在/被删除/无法找到
				if info == TEMP_MSG["PID_DELETED_TEXT"] or info == TEMP_MSG["PID_ERROR_TEXT"]:
					return 

				res = self.db.insert_illust(info)
				if res:
					log_str(TEMP_MSG["INSERT_SUCCESS_INFO"].format(self.class_name,pid))
				else:
					log_str(TEMP_MSG["INSERT_FAIL_INFO"].format(self.class_name,pid))
			# 数据库有该记录
			else:
				# pid不存在/被删除
				if info == TEMP_MSG["PID_DELETED_TEXT"]:
					result = self.db.delete_user_illust(key="pid",value=pid)
					# 删除成功
					if result:
						log_str(TEMP_MSG["DELELE_ILLUST_SUCCESS_INFO"].format(self.class_name,pid))
					else:
						log_str(TEMP_MSG["DELELE_ILLUST_FAIL_INFO"].format(self.class_name,pid))
				else:
					self.db.update_illust(info)
		except Exception as e:
			log_str("thread_by_illust|Exception {}".format(e))

	def run(self):
		log_str(TEMP_MSG["BEGIN_INFO"].format(self.class_name))
		try:
			u_list = self.get_users()
		except Exception as e:
			log_str(e)
			log_str(TEMP_MSG["FOLLOW_ERROR_INFO"].format(self.class_name))
			log_str(TEMP_MSG["SLEEP_INFO"].format(self.class_name))
			return
		else:
			if u_list != []:
				log_str(TEMP_MSG["FOLLOW_SUCCESS_INFO"].format(self.class_name,len(u_list)))
			# 关注列表为空
			elif u_list == []:
				log_str(TEMP_MSG["NO_FOLLOW_USERS"].format(self.class_name))
				return 
			# 未登录
			elif u_list == TEMP_MSG["UL_TEXT"]:
				log_str(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
				exit()

		try:
			pool = ThreadPool(8)
			for i,u in enumerate(u_list):
				all_illust = self.get_user_illust(u)
				if hasattr(self.db,"pool"):
					latest_id = self.db.check_user(u)
					d_total = self.db.get_total(u)
					self.db.update_latest_id(u)
				else:
					latest_id,d_total = 0,0

				position = "({}/{})".format(i+1,len(u_list))
				if u["latest_id"] >= latest_id and d_total < len(all_illust):
					# 满足条件更新
					log_str(TEMP_MSG["UPDATE_USER_INFO"].format(self.class_name,position,u["userName"],u["uid"],len(all_illust),u["latest_id"]))
					# if hasattr(self.db,"pool"):
					# 	self.db.update_latest_id(u)

					for pid in all_illust:
						pool.put(self.thread_by_illust,(pid,),callback)

					time.sleep(5)
				else:
					log_str(TEMP_MSG["NOW_USER_INFO"].format(self.class_name,position,u["userName"],u["uid"],len(all_illust)))
					# 本次更新user无作品
					if u["latest_id"] == -1:
						# 从数据库中删除所有符合u["uid"]的记录
						result = self.db.delete_user_illust(key="uid",value=u["uid"])
						if result:
							log_str(TEMP_MSG["DELELE_USER_ILLUST_SUCCESS_INFO"].format(self.class_name,u["userName"],u["uid"]))
						else:
							log_str(TEMP_MSG["DELELE_USER_ILLUST_FAIL_INFO"].format(self.class_name,u["userName"],u["uid"]))
		except Exception as e:
			log_str("Exception:{}".format(e))
			pool.close()
		finally:
			pool.close()
		log_str(TEMP_MSG["SLEEP_INFO"].format(self.class_name))


# if __name__ == '__main__':
# 	from config import USERS_CYCLE
# 	c = Crawler()
# 	while True:
# 		c.run()
# 		time.sleep(USERS_CYCLE)