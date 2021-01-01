# coding=utf8
import os
import json
import time
import random
from flask import Flask,request,jsonify

from config import API_HOST,API_PORT,RANDOM_LIMIT,API_THREAD
from downer import Down
from logstr import log_str
from message import *


app = Flask(__name__)

# =========================
# TODO APIER分离为apier模块
class APIER:
	def __init__(self):
		self.Downloader = Down()
		self.db = self.Downloader.db

def get_apier():
	log_str("get_apier")
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
			return jsonify({'result':[{"error":False,"message":PARAM_ERROR}]})
			
		# 无传参pid,pid长度异常
		if pid == None or len(pid) > 20:
			return jsonify({'result':[{"error":False,"message":PARAM_ERROR}]})

		# pid小于0
		if int(pid) < 0:
			return jsonify({'result':[{"error":False,"message":PARAM_ERROR}]})

		try:
			# r:list
			r = db.select_illust(pid)
			if r == "" or r == None:
				return jsonify({'result':[{"error":False,"message":NO_DATA_MESSAGE}]})
			else:
				res = r[0]
				res["reverse_url"] = db.pixiv_re_proxy(res)
				# 删除不必要的字段
				del res["urls"],res["path"]
				res["error"],res["message"] = False,""
				log_str(res)
		except Exception as e:
			log_str("Exception: {}".format(e))
			return jsonify({'result':[{"error":True,"message":INTERNAL_ERROR_MESSAGE}]})
		else:
			return jsonify({'result':[res]})

# 随机获取1~10条记录，最多指定2个tag
@app.route('/api/v2/random',methods=['GET','POST'])
def p_random():
	db = apier.db
	# extra指定tag
	if request.method == "POST":
		# 数量
		num = request.form.get('num',1)
		# 指定tag
		ex = request.form.get('extra',None)
		# 指定数据表
		table = request.form.get('table',"bookmark")

		# num为int类型以外的类型
		try:
			int(num)
		except:
			return jsonify({'result':[{"error":False,"message":PARAM_ERROR}]})
			
		# num小于等于0
		if int(num) <= 0:
			return jsonify({'result':[{"error":False,"message":PARAM_ERROR}]})
 
		# 大于单次返回限制
		if int(num) > RANDOM_LIMIT:
			num = 1
		log_str("num:{},tag:{}".format(num,ex))

		# 查询符合条件的所有pid_list
		result_pid_list = db.random_illust(extra=ex,table="bookmark")
		# 数据库查询无结果
		if result_pid_list == []:
			return jsonify({'result':{"error":False,"message":NO_TAG_MESSAGE}})
		log_str("result_pid_list: {}".format(len(result_pid_list)))

		# 数据库查询结果数量小于需求数量
		if len(result_pid_list) < int(num):
			random_pid_list = result_pid_list
		else:
			random_pid_list = random.sample(result_pid_list,int(num))

		res = []
		for _ in random_pid_list:
			r = db.select_illust(_["pid"],table="bookmark")[0]
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
	return API_ADD_ERROR

@app.errorhandler(500)
def error500(error):
	return API_ERROR


# if __name__ == '__main__':
	# app.debug = True
	# app.run(API_HOST,API_PORT)