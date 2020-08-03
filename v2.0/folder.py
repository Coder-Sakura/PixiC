# coding=utf8
import os
import re

from config import ROOT_PATH,BOOKMARK_PATH

class Folder(object):
	def __init__(self):
		# 关注画师路径处理
		self.path = os.path.join(os.getcwd(),"pixiv_crawler") if ROOT_PATH == "" else ROOT_PATH
		isExists = os.path.exists(self.path)
		if not isExists:os.makedirs(self.path)

		# 收藏路径处理,folder类用不到,主要是确保收藏的主目录创建

		self.bk_path = os.path.join(os.getcwd(),"bookmark") if BOOKMARK_PATH == "" else BOOKMARK_PATH
		isExists = os.path.exists(self.bk_path)
		if not isExists:os.makedirs(self.bk_path)

	def select_user_path(self, uid):
		for folder in os.listdir(self.path):
			if str(uid) == folder.split('--')[0]:
				user_path = os.path.join(self.path,folder)
				return user_path

	def mkdir_painter(self, info):
		'''
		创建画师文件夹
		:parmas info 作品数据信息
		:return user_path 画师路径
		'''
		uid = str(info["uid"])
		userName = info["userName"]

		userName = re.sub('[\/:*?"<>|]','_',userName)
		# folder_name = uid + '--' + userName
		painter_name = '--'.join([str(uid),str(userName)])

		# 避免画师更新名字,进行判断id
		for folder in os.listdir(self.path):
			if str(uid) == folder.split('--')[0]:
				user_path = os.path.join(self.path,folder)
				return user_path

		user_path = os.path.join(self.path,painter_name)
		os.makedirs(user_path)
		return user_path

	def mkdir_illusts(self, user_path,pid):
		'''
		创建作品illusts文件夹
		:parmas user_path 画师路径/收藏作品主目录
		:parmas pid 作品id
		:return illusts_id_path 作品路径
		'''
		illusts_id_path = os.path.join(user_path,str(pid))
		isExists = os.path.exists(illusts_id_path)

		if not isExists:
			os.makedirs(illusts_id_path)
			return illusts_id_path
		else:
			return illusts_id_path

file_manager = Folder()