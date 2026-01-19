# coding=utf8
import os
import re
import glob

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

		# uid 到画师目录的内存索引，避免频繁全盘扫描
		self.uid_to_user_path = {}
		self._build_user_index()

	def _build_user_index(self):
		"""
		扫描一次根目录，建立 uid -> user_path 的索引。
		目录命名规则为："{uid}--{userName}"，取 "--" 之前的部分作为 uid。
		"""
		try:
			for folder in os.listdir(self.path):
				# 只索引形如 uid--name 的目录
				if "--" in folder:
					uid_prefix = folder.split('--')[0]
					if uid_prefix.isdigit():
						self.uid_to_user_path[uid_prefix] = os.path.join(self.path, folder)
		except FileNotFoundError:
			# 根目录尚未创建时忽略
			pass

	def select_user_path(self, uid, userName):
		uid_str = str(uid)
		# 优先走内存索引
		user_path = self.uid_to_user_path.get(uid_str)
		if user_path and os.path.exists(user_path):
			return user_path
		# 索引缺失或目录不存在时，重建一次索引
		self._build_user_index()
		user_path = self.uid_to_user_path.get(uid_str)
		if user_path and os.path.exists(user_path):
			return user_path
		# 未找到则创建
		return self.mkdir_painter({"uid":uid,"userName":userName})

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
				# 回填索引
				self.uid_to_user_path[str(uid)] = user_path
				return user_path

		user_path = os.path.join(self.path,painter_name)
		os.makedirs(user_path)
		# 新建后回填索引
		self.uid_to_user_path[str(uid)] = user_path
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
		
	def search_isExistsPid(self,root,extra="c",*args):
		'''
		查找pid是否已下载
		:parmas root 画师路径/收藏作品主目录
		:parmas pid 作品id
		:parmas extra 处理不同模块
		:return True or False 已存在/不存在
		'''
		if extra == "c":
			uid = str(args[0])
			pid = str(args[1])
			# 通过索引快速定位画师目录，避免全盘 glob
			user_path = self.uid_to_user_path.get(uid)
			if not user_path or not os.path.isdir(user_path):
				# 尝试重建索引后再取一次
				self._build_user_index()
				user_path = self.uid_to_user_path.get(uid)
				if not user_path or not os.path.isdir(user_path):
					return False
			illust_dir = os.path.join(user_path, pid)
			if not os.path.isdir(illust_dir):
				return False
			# 仅在该插画目录内局部匹配，提高效率
			flag = glob.glob(os.path.join(illust_dir, f"{pid}*.*"))
			return bool(flag)
		elif extra == "b":
			pid = str(args[0])
			illust_dir = os.path.join(root, pid)
			if not os.path.isdir(illust_dir):
				return False
			flag = glob.glob(os.path.join(illust_dir, f"{pid}*.*"))
			return bool(flag)

		return False


file_manager = Folder()