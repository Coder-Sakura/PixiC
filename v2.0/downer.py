# coding=utf8
"""
封装的下载器,直接调用使用
time: 2020-05-11
author: coder_sakura
"""

import os
import json
import imageio
import time
import zipfile
import requests
# 强制取消警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from config import USERS_LIMIT,BOOKMARK_LIMIT
from db import db_client
from folder import file_manager
from logstr import log_str
from login import client
from message import *
from config import *


class Down(object):
	def __init__(self):
		self.se = requests.session()
		self.client = client
		self.jar = client.set_cookie()
		self.file_manager = file_manager
		self.db = db_client()
		self.headers = {
			# "Connection": "keep-alive",
			"Host": "www.pixiv.net",	# 0416添加
			"referer": "https://www.pixiv.net/",
			"origin": "https://accounts.pixiv.net",
			"accept-language": "zh-CN,zh;q=0.9",	# 返回translation,中文翻译的标签组
			"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
				'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
		}
		# 作品链接
		self.artworks_url = "https://www.pixiv.net/artworks/{}"
		# 作品数据
		self.ajax_illust = "https://www.pixiv.net/ajax/illust/{}"
		# 动图的zip包下载地址
		self.zip_url = "https://www.pixiv.net/ajax/illust/{}/ugoira_meta"
		self.class_name = self.__class__.__name__

	def baseRequest(self, options, data=None, params=None, retry_num=5):
		'''
	    :params options 请求参数    {"method":"get/post","url":"example.com"}
	    :params data
	    :params params
	    :params retry_num 重试次数
	    :return response对象/False

	    如果options中有定义了headers参数,则使用定义的;否则使用init中初始化的headers

	    下面这行列表推导式作用在于：
	    添加referer时,referer需要是上一个页面的url,比如:画师/作品页面的url时,则可以自定义请求头
	    demo如下:
	    demo_headers = headers.copy()
	    demo_headers['referer']  = 'www.example.com'
	    options ={
	        "method":"get",
	        "url":"origin_url",
	        "headers":demo_headers
	    }
	    baseRequest(options=options)
	    这样baseRequest中使用的headers则是定制化的headers,而非init中初始化的默认headers了
	    '''
		# log_str(options["url"])
		base_headers = [options["headers"] if "headers" in options.keys() else self.headers][0]

		try:
	    	# if options["method"].lower() == "get":
	    	# 网络请求函数get、post请求,暂时不判断method字段,待后续更新
			response = self.se.get(
					options["url"],
					data = data,
					params = params,
					cookies = self.jar,
					headers = base_headers,
					verify = False,
					timeout = 10,
				)
			return response
		except  Exception as e:
			if retry_num > 0:
				return self.baseRequest(options,data,params,retry_num-1)
			else:
				log_str(DM_NETWORK_ERROR_INFO.format(self.class_name,options["url"],e))

	def get_illust_info(self, pid, extra=None):
		'''
		:parmas pid: 作品id,int类型
		:parmas extra: 额外模式,用于对各种模式做一些特殊处理
		比如关注画师和收藏作品2个模式之间有些许不同
		默认None,extra为bookmark时,为bookmark模式

		:return data: 作品数据,字典

		不存在的id:https://www.pixiv.net/ajax/illust/78914404
		多图 https://www.pixiv.net/ajax/illust/78997178
		动图 https://www.pixiv.net/ajax/illust/80373423
		单图 https://www.pixiv.net/ajax/illust/77719030
		'''
		info_url = self.ajax_illust.format(pid)
		resp = json.loads(self.baseRequest(options={"url":info_url}).text)
		# 未登录
		if resp["message"] == UNLOGIN_TEXT:
			log_str(UNLOGIN_INFO.format(self.class_name))
			return None

		if resp["error"] == True:
			# 出错则不更新,不下载;
			return None
		
		# 数据
		info = resp["body"]
		uid = int(info["userId"])
		userName = info["userName"]
		purl = self.artworks_url.format(pid)
		try:
			title = info["illustTitle"]
		except:
			title = "None"
		# tag形如魅惑の谷間/魅惑的乳沟、下乳/南半「球」、青雲映す碧波、
		try:
			tag = ""
			for i in info["tags"]["tags"]:
				r = '{}、'.format(i["tag"])
				if "translation" in i.keys():r = "{}/{}、".format(i["tag"],i["translation"]["en"])
				tag += r
		except:
			tag = "None"
		# 作品类型
		illustType = info["illustType"]
		# 页数
		pageCount = info["pageCount"]
		# 0 False,1 True
		is_r18 = [1 if 'R-18' in tag else 0][0]
		# 浏览人数
		viewCount = info["viewCount"]
		# 收藏人数
		bookmarkCount = info["bookmarkCount"]
		# 赞/喜欢人数
		likeCount = info["likeCount"]
		# 评论人数
		commentCount = info["commentCount"]
		# 图片链接组
		# 取数据,json.load(res[0]["urls"])
		urls = str(info["urls"])
		# 原图链接
		original = info["urls"]["original"]
		# 作品数据
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
			"viewCount":viewCount,
			"bookmarkCount":bookmarkCount,
			"likeCount":likeCount,
			"commentCount":commentCount,
			"urls":urls,
			"original":original
		}
		# extra对模式处理
		if extra == "bookmark":
			LIMIT = BOOKMARK_LIMIT
			user_path = file_manager.bk_path
		else:
			user_path = self.file_manager.select_user_path(uid)
			LIMIT = USERS_LIMIT


		"""
		判断下载筛选条件
		满足条件   --> 下载器 path=file_manager 入库
		不满足条件 -->  ---      path=None      入库
		"""
		# 获取作品下载路径
		# if bookmarkCount > 0:
		# 336个画师,作品全下载共120G+
		# 限制收藏>3000,共45G
		if bookmarkCount > LIMIT:
			path = self.file_manager.mkdir_illusts(user_path,pid)
			data["path"] = path
			# 下载器启动
			# log_str("id:{} 作品正在下载".format(pid))
			self.filter(data)
		else:
			path = "None"
			data["path"] = path
			# log_str("id:{} 作品不满足条件,不下载".format(pid))

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
			# log_str("{}已存在".format(name))
			pass
		else:
			c = self.baseRequest(options={"url":original}).content
			size = self.downSomething(illustPath,c)
			log_str(DM_DOWNLOAD_SUCCESS_INFO.format(self.class_name,name,self.size2Mb(size)))
			time.sleep(1)

	def illustMulti(self, data):
		"""
		下载filter判定的多图id
		:param data: 作品数据
		:return: 
		"""
		pageCount = data["pageCount"]
		original = data["original"]
		path_ = data["path"]

		# original = "https://i.pixiv.cat/img-original/img/2020/01/20/04/13/16/78997178_p0.png"
		# 正序查找,获取"."前面数字的索引 | ['i', 'v', '0'] 取最后一个
		# n记录original中变化页数的索引
		n = [i-1 for i in range(len(original)-1) if original[i] == "."][-1]
		
		# 倒序切分1次,以p0的0进行切分
		# end = original.rsplit(original[n],1)
		
		for i in range(0,int(pageCount)):
			# 用join方法将页数合成进新的url
			# new_original = "{}".join(end).format(i)
			# 倒序替换时,插入的页数也需要反转str(i)[::-1]
			new_original = original[::-1].replace(original[n],str(i)[::-1],1)[::-1]
			name = "{}-{}.{}".format(data["pid"],i,new_original.split(".")[-1])
			illustPath = os.path.join(path_,name)

			if os.path.exists(illustPath) == True and os.path.getsize(illustPath) > 1000:
				# log_str("{}已存在".format(name))
				pass
			else:
				c = self.baseRequest(options={"url":new_original}).content
				size = self.downSomething(illustPath,c)
				log_str(DM_DOWNLOAD_SUCCESS_INFO.format(self.class_name,name,self.size2Mb(size)))
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
			# log_str("{}已存在".format(name))
			pass
		else:
			z = json.loads(self.baseRequest(options={"url":zipInfoUrl}).text)
			zip_url = z["body"]["originalSrc"]
			# item["delay"]为对应图片停留间隔,单位毫秒
			delay = [item["delay"]/1000 for item in z["body"]["frames"]]
			# 下载zip
			with open(zip_path,"ab") as f1:
				f1.write(self.baseRequest(options={"url":zip_url}).content)
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
			log_str(DM_DOWNLOAD_SUCCESS_INFO.format(self.class_name,name,self.size2Mb(size)))
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


# Downloader = Down()