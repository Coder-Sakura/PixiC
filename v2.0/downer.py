# coding=utf8
"""
封装的下载器,直接调用使用
time: 2020-05-11
author: coder_sakura
"""

import os
import json
import time
import random
import imageio
import zipfile
import requests
# 强制取消警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from config import USERS_LIMIT,BOOKMARK_LIMIT
from db import db_client
from folder import file_manager
from log_record import logger
from login import client
from message import TEMP_MSG


# class Down(object):
class Downloader:
	def __init__(self):
		self.class_name = self.__class__.__name__
		self.se = requests.session()
		self.client = client
		self.cookie_list = client.subprocess_check()
		self.file_manager = file_manager
		self.db = db_client()
		self.headers = {
			# "Connection": "keep-alive",
			"Host": "www.pixiv.net",
			"referer": "https://www.pixiv.net/",
			"origin": "https://accounts.pixiv.net",
			"accept-language": "zh-CN,zh;q=0.9",	# 返回translation,中文翻译的标签组
			"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
				'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
		}
		# 作品链接
		self.artworks_url = "https://www.pixiv.net/artworks/{}"
		# 作品数据 8.16
		# self.ajax_illust = "https://www.pixiv.net/ajax/illust/{}"
		self.ajax_illust = "https://www.pixiv.net/touch/ajax/illust/details?illust_id={}"
		self.ajax_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "",
            "Connection": "keep-alive",
        }
		# 动图的zip包下载地址
		self.zip_url = "https://www.pixiv.net/ajax/illust/{}/ugoira_meta"
		# 多图-每张图的url组
		self.multi_url = "https://www.pixiv.net/ajax/illust/{}/pages"

		# print("user_id",self.client.user_id)

	def baseRequest(self, options, data=None, params=None, retry_num=5):
		'''
	    :params options: 请求参数,暂时只用到headers和url
	    :params data: Post
	    :params params: Get
	    :params retry_num: 重试次数
	    :return: response对象/False

	    列表推导式作用在于: 优先使用options中的headers,否则使用self.headers
	    比如:添加referer,referer需要是上一个页面的url,则可以自定义请求头
	    demo_headers = headers.copy()
	    demo_headers['referer']  = 'www.example.com'
	    options ={"url":"origin_url","headers":demo_headers}
	    baseRequest(options=options)
	    '''
		base_headers = [options["headers"] if "headers" in options.keys() else self.headers][0]

		try:
			# if options["method"].lower() == "get":
			# 网络请求函数get、post请求,暂时不判断method字段,待后续更新
			# logger.debug("cookie_list {}".format(len(self.cookie_list)))
			response = self.se.get(
	    			options["url"],
	    			data = data,
	    			params = params,
	    			cookies = random.choice(self.cookie_list),
	    			headers = base_headers,
	    			verify = False,
	    			timeout = 10,
				)
			return response
		except  Exception as e:
			if retry_num > 0:
				logger.warning(TEMP_MSG["DM_RETRY_INFO"].format(options["url"]))
				time.sleep(1)
				return self.baseRequest(options,data,params,retry_num-1)
			else:
				logger.warning(TEMP_MSG["DM_NETWORK_ERROR_INFO"].format(self.class_name,options,e))
				return None

	def get_illust_info(self, pid, extra="pixiv"):
		'''
		整合作品数据
		:parmas pid: 作品id,int类型
		:parmas extra: 对不同模块设置对应的下载限制和拼接本地路径
		:return data: 作品数据,字典

		不存在的id:https://www.pixiv.net/ajax/illust/78914404
		多图 https://www.pixiv.net/ajax/illust/78997178
		动图 https://www.pixiv.net/ajax/illust/80373423
		单图 https://www.pixiv.net/ajax/illust/77719030
		'''
		info_url = self.ajax_illust.format(pid)
		# r = self.baseRequest(options={"url":info_url})
		# 8.16 issues #14
		r = self.baseRequest(options={"url":info_url, "headers":self.ajax_headers})
		if r == None:
			return None

		# json解析错误
		try:
			resp = json.loads(r.text)
		except json.decoder.JSONDecodeError as e:
			logger.warning(TEMP_MSG["JSON_DECODE_ERR"].format(r.text))
			return None

		# 未登录
		if resp["message"] == TEMP_MSG["UNLOGIN_TEXT"]:
			logger.warning(TEMP_MSG["UNLOGIN_INFO"].format(self.class_name))
			return None

		# 出错则不更新不下载;
		if resp["error"] == True:
			# 判断其他状态
			# 作品被删除--该作品已被删除，或作品ID不存在。
			if resp["message"] == TEMP_MSG["PID_DELETED_TEXT"]:
				logger.warning(f'{TEMP_MSG["PID_DELETED_TEXT"]} - {pid}')
				return TEMP_MSG["PID_DELETED_TEXT"]

			# pid错误--无法找到您所请求的页面
			elif resp["message"] ==  TEMP_MSG["PID_ERROR_TEXT"]:
				logger.warning(f'{TEMP_MSG["PID_ERROR_TEXT"]} - {pid}')
				return TEMP_MSG["PID_ERROR_TEXT"]

			# 作品被设为私密--尚无权限浏览该作品
			elif resp["message"] ==  TEMP_MSG["PID_UNAUTH_ACCESS"]:
				logger.warning(f'{TEMP_MSG["PID_UNAUTH_ACCESS"]} - {pid}')
				return TEMP_MSG["PID_UNAUTH_ACCESS"]
				
			elif resp["message"] ==  TEMP_MSG["LIMIT_TEXT"]:
				return TEMP_MSG["LIMIT_TEXT"]

		# 作品数据
		info = resp["body"]
		# uid
		uid = int(info["author_details"]["user_id"])
		# userName
		userName = info["author_details"]["user_name"]
		# artworks_url
		purl = self.artworks_url.format(pid)
		# title
		title = info["illust_details"]["alt"]
		# tag形如<作者名称>、魅惑の谷間/魅惑的乳沟、下乳/南半「球」、青雲映す碧波
		try:
			tag_list = []
			for i in info["illust_details"]["display_tags"]:
				if "translation" in i.keys():
					r = "{}/{}".format(i["tag"],i["translation"])
				else:
					r = i["tag"]
				if r != "":
					tag_list.append(r)
			tag = "、".join(tag_list)
		except:
			tag = ""
		finally:
			# 添加作者名称
			tag  = "{}、".format(userName) + tag
		# 作品类型
		illustType = int(info["illust_details"]["type"])
		# 页数
		pageCount = int(info["illust_details"]["page_count"])
		# 是否为R-18
		is_r18 = [1 if 'R-18' in tag else 0][0]
		# 浏览人数
		viewCount = int(info["illust_details"]["rating_view"])
		# 收藏人数
		bookmarkCount = int(info["illust_details"]["bookmark_user_total"])
		# 赞/喜欢人数
		likeCount = int(info["illust_details"]["rating_count"])
		# 评论人数 新接口无该字段
		commentCount = 0
		# 图片链接组
		urls = {
			"mini": info["illust_details"]["url_ss"],
			"thumb": info["illust_details"]["url_s"],
			"small": info["illust_details"]["url_placeholder"].replace("100x100", "540x540_70"),
			"regular": info["illust_details"]["url"],
			"original": info["illust_details"]["url_big"]
		}
		urls = str(urls)
		# 原图链接
		original = info["illust_details"]["url_big"]
		# score&illust_level
		score = round((bookmarkCount/viewCount),3)
		illust_level = self.get_illust_level(score,bookmarkCount)

		# 整合的作品数据
		data = {
			"uid":uid,
			"userName":userName,
			"pid":int(pid),
			"purl":purl,
			"title":title,
			"tag":tag,
			"pageCount":pageCount,
			"illustType":illustType,
			"is_r18":is_r18,
			"score":score,
			"illust_level":illust_level,
			"viewCount":viewCount,
			"bookmarkCount":bookmarkCount,
			"likeCount":likeCount,
			"commentCount":commentCount,
			"urls":urls,
			"original":original,
		}

		# 根据extra字段获取对应的LIMIT和user_path
		# bookmark表
		if extra == "bookmark":
			LIMIT = BOOKMARK_LIMIT
			user_path = file_manager.bk_path
		# pixiv表
		elif extra == "pixiv":
			LIMIT = USERS_LIMIT
			user_path = self.file_manager.select_user_path(uid,userName)

		# 判断下载筛选条件,获取作品下载路径
		# 满足条件   --> 下载器 path=file_manager 入库
		# 不满足条件 -->  ---      path=None      入库
		if bookmarkCount > LIMIT:
			path = self.file_manager.mkdir_illusts(user_path,pid)
			data["path"] = path
			# 下载器启动
			logger.info("id:{} 作品正在下载".format(pid))
			self.filter(data)
		else:
			path = "None"
			data["path"] = path
			# logger.info("id:{} 作品不满足条件,不下载".format(pid))

		return data

	def filter(self, data):
		"""
		根据pageCount和illustType判定作品id类型
		:param data: 作品数据
		:return:

		======以下为判定规则========
				  单图 多图 动图 漫画单图 漫画多图
		pageCount  1	 n 	  1    1      n
		illustType 0	 0 	  2    1	  1
		===========================
		"""
		pageCount = data["pageCount"]
		illustType = data["illustType"]

		if pageCount == 1:
			if illustType == 2:
				self.illustGif(data)
			else:
				self.illustSingle(data)
		else:
			self.illustMulti(data)

	def illustSingle(self, data):
		"""
		下载filter判定的单图id
		:param data: 作品数据
		:return:
		"""
		original = data["original"]
		path_ = data["path"]
		name = "{}.{}".format(data["pid"],original.split(".")[-1])
		illustPath = os.path.join(path_,name)

		if os.path.exists(illustPath) == True and os.path.getsize(illustPath) > 1000:
			# 作品存在且大于1000字节,为了避免58字节错误页面和其他错误页面
			# logger.info("{}已存在".format(name))
			pass
		else:
			c = self.baseRequest(options={"url":original})
			if c == None:
				return None
			size = self.downSomething(illustPath,c.content)
			logger.success(TEMP_MSG["DM_DOWNLOAD_SUCCESS_INFO"].format(self.class_name,name,self.size2Mb(size)))
			time.sleep(1)

	def illustMulti(self, data):
		"""
		下载filter判定的多图id
		:param data: 作品数据
		:return: 
		"""
		path_ = data["path"]
		multi_resp = self.baseRequest(options={"url":self.multi_url.format(data["pid"])})
		if multi_resp == None:
			return None

		multi_json = json.loads(multi_resp.text)
		if multi_json["error"] == True or multi_json["body"] == []:
			logger.info(TEMP_MSG["ILLUST_EMPTY_INFO"].format(self.class_name,data["pid"]))
			return None
		
		for m in multi_json["body"]:
			# https://i.pixiv.cat/img-original/img/2020/01/20/04/13/16/78997178_p0.png
			new_original = m["urls"].get("original","")
			# 78997178-0.png
			name = new_original.split("/")[-1].replace("_p","-")
			illustPath = os.path.join(path_,name)
			if os.path.exists(illustPath) == True and os.path.getsize(illustPath) > 1000:
				# logger.debug("{}已存在".format(name))
				pass
			else:
				c = self.baseRequest(options={"url":new_original})
				if c == None:
					return None
				size = self.downSomething(illustPath,c.content)
				logger.success(TEMP_MSG["DM_DOWNLOAD_SUCCESS_INFO"].format(self.class_name,name,self.size2Mb(size)))
				time.sleep(1)

	def illustGif(self, data):
		"""
		下载filter判定的动图图id
		:param data: 作品数据
		:return: 
		"""
		path_ = data["path"]
		# 动图info url
		zipInfoUrl = self.zip_url.format(data["pid"])
		zip_name = "{}.zip".format(data["pid"])
		zip_path = os.path.join(path_,zip_name)
		# 存储需要合成gif的图片列表
		frames = []
		name = "{}.gif".format(data["pid"])
		illustPath = os.path.join(path_,name)

		if os.path.exists(illustPath) == True and os.path.getsize(illustPath) > 1000:
			# logger.debug("{}已存在".format(name))
			pass
		else:
			z_info = self.baseRequest(options={"url":zipInfoUrl})
			if z_info == None:
				return None

			z = json.loads(z_info.text)
			zip_url = z["body"]["originalSrc"]
			# item["delay"]为对应图片停留间隔,单位毫秒
			delay = [item["delay"]/1000 for item in z["body"]["frames"]]

			# 下载zip
			zip_resp = self.baseRequest(options={"url":zip_url})
			if zip_resp == None:
				return None

			with open(zip_path,"ab") as f1:
				f1.write(zip_resp.content)

			# 解压zip
			with zipfile.ZipFile(zip_path,"r") as f2:
				for file in f2.namelist():
					f2.extract(file,path_)

			# 删除zip
			os.remove(zip_path)
			# 扫描解压出来的图片
			files = [os.path.join(path_,i) for i in os.listdir(path_)]
			# 添加图片到待合成列表
			for i in range(1,len(files)):
				frames.append(imageio.imread(files[i]))
			# 合成gif
			imageio.mimsave(illustPath,frames,duration=delay)
			# 下载成功
			size = os.path.getsize(illustPath)
			logger.success(TEMP_MSG["DM_DOWNLOAD_SUCCESS_INFO"].format(self.class_name,name,self.size2Mb(size)))
			# 删除解压出来的图片
			for j in files:
				os.remove(os.path.join(path_,j))
			time.sleep(1)

	def downSomething(self, path, content):
		"""
		二进制数据写入图片
		:params path: 图片路径
		:params content: 二进制数据
		:return : 写入大小
		"""
		# name考虑切分,或者传参进来
		with open(path,"wb") as f:
			f.write(content)
		return os.path.getsize(path)

	def size2Mb(self, size):
		"""
		:params size: 文件大小,字节数
		:return: 
		"""
		if size/1024 > 1024:
			return "%.3fMb" %(size/1024/1024)
		else:
			return "%.3fKb" %(size/1024)

	def get_illust_level(self,score,bookmarkCount):
		"""
		根据score及bookmarkCount确认作品评分等级,默认为R
		
		:params score: 得分,bookmarkCount/viewCount -> float
		:params bookmarkCount: 收藏数 -> int
		:return: 'R','SR','SSR','UR'其中一个,不满足则默认R -> str
		"""
		# 判断评分等级
		illust_level_list = ['R','SR','SSR','UR']
		# 评分区间右侧边界值
		illust_interval = {'R':0.140,'SR':0.260,'SSR':0.325,'UR':1.000}
		illust_default_level = "R"
		illust_level = ""

		# === 针对浏览量大的热门作品 ===
		# 从R中寻找SSR,不取边界值
		if 20000 < bookmarkCount and score < illust_interval['R']:
			illust_level = illust_level_list[2]

		# 从SR中寻找UR,不取边界值
		if 25000 < bookmarkCount and illust_interval['R'] < score < illust_interval['SR']:
			illust_level = illust_level_list[3]

		# 上述规则满足则返回illust_level
		if illust_level:
			return illust_level

		# === 基本评分等级判定 ===
		# R
		if 0 <= score < illust_interval['R']:
			illust_level = illust_level_list[0]
		# SR
		elif illust_interval['R'] <= score < illust_interval['SR']:
			illust_level = illust_level_list[1]
		# SSR
		elif illust_interval['SR'] <= score < illust_interval['SSR']:
			illust_level = illust_level_list[2]
		# UR
		elif illust_interval['SSR'] <= score <= illust_interval['UR']:
			illust_level = illust_level_list[3]

		# 6条规则都不满足则默认返回R
		if not illust_level:
			logger.info("采取默认规则 score:{} bookmarkCount:{}".format(score,bookmarkCount))
			return illust_default_level
		return illust_level

# Downloader = Down()