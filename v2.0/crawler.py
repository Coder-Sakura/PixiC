# coding=utf8
"""
关注画师爬虫
time: 2020-05-11
author: coder_sakura
"""
import json
import time
import re

from config import SKIP_ISEXISTS_ILLUST,ROOT_PATH
from downer import Downloader
from log_record import logger
from message import TEMP_MSG
from thread_pool import ThreadPool,callback
from tag import TAG_FLAG_USER
from ptimer import Timer


class Crawler(object):
	def __init__(self):
		self.Downloader = Downloader()
		self.user_id = self.Downloader.client.user_id
		self.base_request = self.Downloader.baseRequest

		# 公开/非公开 见get_page_users
		self.rest_list = ["show", "hide"]
		# 画师列表
		self.follw_url = "https://www.pixiv.net/ajax/user/{}/following".format(self.user_id)
		# 作品链接,存数据库
		self.artworks_url = "https://www.pixiv.net/artworks/{}"
		# 画师作品列表
		self.all_illust_url = "https://www.pixiv.net/ajax/user/{}/profile/all"
		self.file_manager = self.Downloader.file_manager
		self.db = self.Downloader.db
		self.class_name = self.__class__.__name__

	def get_page_users(self, offset, rest="show"):
		"""
		:params offset 偏移量,按照偏移量获得limit范围内的画师
		:return 接口数据中的画师数组
		"""
		params = {
			"offset": offset,
			"limit": 100,
			"rest": rest,			
		}
		try:
			r = json.loads(self.base_request({"url":self.follw_url},params=params).text)
		except Exception as e:
			# 网络请求出错
			logger.warning(TEMP_MSG["FOLLOW_PAGE_ERROR_INFO"].format(self.class_name,offset,offset+100))
			logger.warning(f"<Exception> - {e}")
			return None
		else:
			# 未登录
			if r["message"] == TEMP_MSG["UNLOGIN_TEXT"]:
				logger.warning(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
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

					# 画师/用户无作品
					if u["illusts"] == []:
						user_info["latest_id"] = -1
						logger.warning(TEMP_MSG["FOLLOW_NO_ILLUSTS_INFO"].format(self.class_name,u["userName"],u["userId"]))
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
			logger.warning(TEMP_MSG["FOLLOW_DATA_ERROR_INFO"].format(self.class_name,e))
			return []
		else:
			return user_illust_list

	def check_account_byDB(self):
		if hasattr(self.db,"pool") == False:
			return 

		_index_id = 1
		_limit = 100
		logger.info("check_account_byDB START.")

		while True:
			db_user_data = self.db.select_user(start_id=_index_id, table="pxusers")
			# 数据表无数据返回
			if not db_user_data:
				logger.info("check_account_byDB END.")
				break
			else:
				for _user_data in db_user_data:
					illust_url = self.all_illust_url.format(_user_data["uid"])
					try:
						u_json = json.loads(self.base_request({"url":illust_url}).text)
					except json.decoder.JSONDecodeError:
						u_json = {"error":False, "message":"", "body":[]}

					# 已注销账户
					if u_json.get("error",False) and \
						TEMP_MSG["USER_LEAVE_PIXIV_INFO_CN"] in u_json["message"] and \
						not u_json["body"]:
						logger.warning(f"""DELETE {_user_data["uid"]} | {_user_data["userName"]} records in """\
							"""TABLES - pixiv /bookmark /pxusers""")
						self.db.delete_user_illust(key="uid",value=_user_data["uid"],table="pixiv")
						self.db.delete_user_illust(key="uid",value=_user_data["uid"],table="bookmark")
						self.db.delete_user_illust(key="uid",value=_user_data["uid"],table="pxusers")
					
					_index_id += _limit

	def thread_by_illust(self, *args):
		"""
		线程任务函数
		"""
		pid = args[0]
		uid = args[1]
		info = None
		
		# 跳过已下载插画的请求
		if SKIP_ISEXISTS_ILLUST and self.file_manager.search_isExistsPid(
			ROOT_PATH,"c",*(uid,pid,)):
			logger.info(f"SKIP_ISEXISTS_ILLUST - {uid} - {pid}")
			return info

		try:
			info = self.Downloader.get_illust_info(pid)
		except Exception as e:
			logger.warning(TEMP_MSG["ILLUST_NETWORK_ERROR_INFO"].format(self.class_name,pid,e))
			logger.warning(f"{pid} INFO:{info}")
			return info

		if not info:
			logger.warning(TEMP_MSG["ILLUST_EMPTY_INFO"].format(self.class_name,pid))
			return info

		if info == TEMP_MSG["LIMIT_TEXT"]:
			logger.warning(TEMP_MSG["LIMIT_TEXT_RESP"].format(pid))
			timer = Timer()
			timer.Downloader = self.Downloader
			timer.pid = pid
			timer.extra = "pixiv"
			try:
				info = timer.waiting(info)
			except Exception as e:
				logger.warning(f"Exception - {e} - {info}")
			logger.success(f"共休眠{timer._time}秒,重新恢复访问")

		# 数据库开关关闭
		if hasattr(self.db,"pool") == False:
			return info

		try:
			isExists,path = self.db.check_illust(pid)
			# 数据库无该记录
			if isExists == False:
				# 第一次更新,pid不存在/被删除/无法找到
				if info == TEMP_MSG["PID_DELETED_TEXT"] or info == TEMP_MSG["PID_ERROR_TEXT"]:
					return 

				res = self.db.insert_illust(info)
				if res:
					logger.success(TEMP_MSG["INSERT_SUCCESS_INFO"].format(self.class_name,pid))
				else:
					logger.warning(TEMP_MSG["INSERT_FAIL_INFO"].format(self.class_name,pid))
			# 数据库有该记录
			else:
				# pid不存在/已删除/已设为私密/无权限访问
				if info == TEMP_MSG["PID_DELETED_TEXT"] or\
					info == TEMP_MSG["PID_UNAUTH_ACCESS"]:
					result = self.db.delete_user_illust(key="pid",value=pid)
					# 删除成功
					if result:
						logger.success(TEMP_MSG["DELELE_ILLUST_SUCCESS_INFO"].format(self.class_name,pid))
					else:
						logger.warning(TEMP_MSG["DELELE_ILLUST_FAIL_INFO"].format(self.class_name,pid))
				else:
					self.db.update_illust(info)
		except Exception as e:
			logger.warning("thread_by_illust|Exception {}".format(e))
			logger.warning(f"{pid} INFO:{info}")

	@logger.catch
	def run(self):
		# 开始工作
		TAG_FLAG_USER = False
		logger.info(TEMP_MSG["BEGIN_INFO"].format(self.class_name))
		try:
			u_list = self.get_users()
		except Exception as e:
			logger.warning(TEMP_MSG["FOLLOW_ERROR_INFO"].format(self.class_name))
			logger.warning(f"<Exception> - {e}")
			logger.warning(TEMP_MSG["SLEEP_INFO"].format(self.class_name))
			return
		else:
			if u_list != []:
				logger.success(TEMP_MSG["FOLLOW_SUCCESS_INFO"].format(self.class_name,len(u_list)))
			# 关注列表为空
			elif u_list == []:
				logger.warning(TEMP_MSG["NO_FOLLOW_USERS"].format(self.class_name))
				return 
			# 未登录
			elif u_list == TEMP_MSG["UL_TEXT"]:
				logger.warning(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
				exit()

		pool = ThreadPool(8)
		try:
			# 任务:获取关注列表
			for i,u in enumerate(u_list):
				all_illust = self.get_user_illust(u)
				if hasattr(self.db,"pool"):
					latest_id = self.db.check_user(u)
					d_total = self.db.get_total(u)
					self.db.update_latest_id(u)
				else:
					latest_id,d_total = 0,0

				position = "({}/{})".format(i+1,len(u_list))
				# 满足作品更新条件
				if u["latest_id"] >= latest_id and d_total < len(all_illust):
					# 满足条件更新
					logger.info(TEMP_MSG["UPDATE_USER_INFO"].format(self.class_name,position,u["userName"],u["uid"],len(all_illust),u["latest_id"]))
					# if hasattr(self.db,"pool"):
					# 	self.db.update_latest_id(u)

					for pid in all_illust:
						pool.put(self.thread_by_illust,(pid,u["uid"],),callback)

					# 固定休眠
					time.sleep(5)
				# 无作品更新
				else:
					logger.info(TEMP_MSG["NOW_USER_INFO"].format(self.class_name,position,u["userName"],u["uid"],len(all_illust)))
					# 画师/用户未注销账号 - 无作品
					if u["latest_id"] == -1 and hasattr(self.db,"pool") == True:
						# 删除对应uid的插画数据 - pixiv
						result = self.db.delete_user_illust(key="uid",value=u["uid"],table="pixiv")
						# 删除对应uid的插画数据 - bookmark
						# 修复<random>API接口使用<bookmark>表会返回在pixiv已被删除的pid
						result = self.db.delete_user_illust(key="uid",value=u["uid"],table="bookmark")
						if result:
							logger.success(TEMP_MSG["DELELE_USER_ILLUST_SUCCESS_INFO"].format(self.class_name,u["userName"],u["uid"]))
						else:
							logger.warning(TEMP_MSG["DELELE_USER_ILLUST_FAIL_INFO"].format(self.class_name,u["userName"],u["uid"]))
		except Exception as e:
			logger.warning("Exception:{}".format(e))
			pool.close()
		finally:
			pool.close()
			# 完成工作
			TAG_FLAG_USER = True

		# 任务:对已注销画师/用户的数据进行删除
		self.check_account_byDB()
		# ======================================

		logger.info("="*48)
		logger.info(TEMP_MSG["SLEEP_INFO"].format(self.class_name))


# if __name__ == '__main__':
# 	from config import USERS_CYCLE
# 	c = Crawler()
# 	while True:
# 		c.run()
# 		time.sleep(USERS_CYCLE)