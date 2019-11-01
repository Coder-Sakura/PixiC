import os
import re

from config import ROOT_PATH

class Folder(object):
	def __init__(self):
		self.path = os.getcwd() if ROOT_PATH == None else ROOT_PATH
		isExists = os.path.exists(self.path)
		if not isExists:
			os.makedirs(self.path)

	def mkdir_painter(self,painter_id,name):
		'''
		创建画师文件夹
		'''
		name = re.sub('[\/:*?"<>|]','_',name)
		# folder_name = painter_id + '--' + name
		painter_name = '--'.join([str(painter_id),str(name)])

		# 避免画师更新名字,进行判断id
		for folder in os.listdir(self.path):
			if painter_id == folder.split('--')[0]:
				print(u'[名字叫{}文件夹已存在！]'.format(painter_name))
				painter_path = os.path.join(self.path,folder)
				os.chdir(painter_path) # 切换到目录
				return painter_path

		print(u'[建了一个{}文件夹！]'.format(painter_name))
		painter_path = os.path.join(self.path,painter_name)
		os.makedirs(painter_path)
		os.chdir(painter_path) # 切换到目录
		return painter_path

	def mkdir_illusts(self,painter_path,illusts_id):
		'''
		创建作品illusts文件夹
		'''
		illusts_id_path = os.path.join(painter_path,str(illusts_id))
		isExists = os.path.exists(illusts_id_path)

		if not isExists:
			print(u'\n[在',os.getcwd(),'下建了一个', illusts_id, u'文件夹！]')
			os.makedirs(illusts_id_path)
			os.chdir(illusts_id_path) ##切换到目录
			return illusts_id_path
		else:
			print(u'\n[在',os.getcwd(),'下已经有', illusts_id, u'文件夹！]')
			os.chdir(illusts_id_path) ##切换到目录
			return illusts_id_path