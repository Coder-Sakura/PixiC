# coding=utf8
import os
import json
import time
import random
from flask import Flask,request,jsonify

from config import API_HOST,API_PORT,RANDOM_LIMIT,API_THREAD
from downer import Down
from logstr import log_str
from message import TEMP_MSG


app = Flask(__name__)

# =========================
# TODO APIER可分离为apier模块
class APIER:
	def __init__(self):
		self.Downloader = Down()
		self.db = self.Downloader.db

def get_apier():
	# log_str("get_apier")
	if not hasattr(resource, 'apier'):
		resource["apier"] = APIER()
	return resource["apier"]

resource = {}
apier = get_apier()


# 首页
@app.route('/api/v2')
def index():
	return "<h2>Now it's {}, Welcome To PixiC API!</h2>".format(time.strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/api/v2/get-info',methods=['GET','POST'])
def get_info():
	"""
	查询指定pid的信息
	"""
	db = apier.db
	if request.method == "POST":
		pid = request.form.get('pid',None)

		# pid为int类型以外的
		try:
			int(pid)
		except:
			return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})
			
		# 无传参pid,pid长度异常
		if pid == None or len(pid) > 20:
			return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})

		# pid小于0
		if int(pid) < 0:
			return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})

		try:
			# r:list
			r = db.select_illust(pid)
			if r == "" or r == None:
				return jsonify({'result':[{"error":False,"message":TEMP_MSG["NO_DATA_MESSAGE"]}]})
			else:
				res = r[0]
				res["reverse_url"] = db.pixiv_re_proxy(res)
				# 删除不必要的字段
				del res["urls"],res["path"]
				res["error"],res["message"] = False,""
				log_str(res)
		except Exception as e:
			log_str("Exception: {}".format(e))
			return jsonify({'result':[{"error":True,"message":TEMP_MSG["INTERNAL_ERROR_MESSAGE"]}]})
		else:
			return jsonify({'result':[res]})

# 随机获取1~10条记录，最多指定2个tag
@app.route('/api/v2/random',methods=['GET','POST'])
def random_info():
	db = apier.db
	if request.method == "POST":
		# 数量
		num = request.form.get('num',1)
		# 指定tag
		ex = request.form.get('extra',None)
		# 指定最小收藏数,如:'1000'
		limit = request.form.get('limit',None)
		# 指定评分区间,如指定作品在R,SR之中
		illust_level = request.form.get('illust_level',None)
		# 指定数据表
		table = request.form.get('table',"bookmark")

		# === num ===
		# num可转化为int类型
		try:
			int(num)
		except:
			return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})
		# num <= 0
		if int(num) <= 0:
			return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})
		# 大于单次返回限制
		if int(num) > RANDOM_LIMIT:
			num = 1
		# === num ===

		# === limit ===
		# limit -> None 直接传参即可
		if limit:
			# limit可转化为int类型
			try:
				int(limit)
			except:
				return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})
			# limit <= 0
			if int(limit) <= 0:
				return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})
		# === limit ===

		# === extra ===
		if type(ex) != type("test") and ex:
			print(1)
			return jsonify({'result':[{"error":False,"message":TEMP_MSG["PARAM_ERROR"]}]})
		# === extra ===

		log_str("num:{},ex:{},limit:{},illust_level:{},table:{}".format(num,ex,limit,illust_level,table))
		# 查询符合条件的所有pid_list
		result_pid_list = db.random_illust(extra=ex,limit=limit,illust_level=illust_level,table=table)

		log_str("result_pid_list: {}".format(len(result_pid_list)))
		# 数据库查询无结果
		if result_pid_list == []:
			return jsonify({'result':{"error":False,"message":TEMP_MSG["NO_TAG_MESSAGE"]}})

		# 数据库查询结果数量小于需求数量
		if len(result_pid_list) < int(num):
			random_pid_list = result_pid_list
		else:
			random_pid_list = random.sample(result_pid_list,int(num))

		res = []
		for _ in random_pid_list:
			r = db.select_illust(_["pid"],table=table)[0]
			# 删除不必要的字段
			del r["urls"],r["path"]
			r["reverse_url"] = db.pixiv_re_proxy(r)
			r["error"],r["message"] = False,""
			res.append(r)

		res = [dict(t) for t in set([tuple(d.items()) for d in res])]
		log_str(res)
		return jsonify({'result':res,'count':len(result_pid_list)})

# TODO 查询数据库数据表中是否有对应字段的记录
@app.route('/api/v2/check_item',methods=['GET','POST'])
def check_item():
	db = apier.db
	if request.method == "POST":
		# 
		key = request.form.get('key',"")
		value = request.form.get('value',"")
		table = request.form.get('table',"")
		database = request.form.get('database',None)

		result = db.check_illust(value,key,table,database)
		return jsonify({'result':[{"error":False,"message":result[0]}]})

# TODO 向数据库插入数据
@app.route('/api/v2/i-db',methods=['GET','POST'])
def insert2db():
	pass

@app.errorhandler(404)
def error404(error):
	return TEMP_MSG["API_ADD_ERROR"]

@app.errorhandler(500)
def error500(error):
	return TEMP_MSG["API_ERROR"]


# if __name__ == '__main__':
	# app.debug = True
	# app.run(API_HOST,API_PORT)