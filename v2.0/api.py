# coding=utf8
# import os
import json
import time
import random
from flask import Flask,request,jsonify

# from config import API_HOST,API_PORT,RANDOM_LIMIT,API_THREAD
from config import RANDOM_LIMIT
from downer import Downloader
from log_record import logger
from message import TEMP_MSG


app = Flask(__name__)

# =========================
# TODO APIER可分离为apier模块
class APIER:
	def __init__(self):
		self.Downloader = Downloader()
		self.db = self.Downloader.db

def get_apier():
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
		# 指定数据表
		table = request.form.get('table',"bookmark")
		logger.info(f"Params | <pid> - {pid} | <table> - {table}")

		# pid为int类型以外的
		try:
			int(pid)
		except:
			message = TEMP_MSG["PARAM_ERROR"].format("pid", pid)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})
			
		# 无传参pid,pid长度异常
		if pid == None or len(pid) > 20:
			message = TEMP_MSG["PARAM_ERROR"].format("pid", pid)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})

		# pid小于0
		if int(pid) < 0:
			message = TEMP_MSG["PARAM_ERROR"].format("pid", pid)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})

		try:
			# r:list
			r = db.select_illust(pid=pid,table=table)
			logger.debug(r)
			if r == "" or r == None:
				message = TEMP_MSG["NO_DATA_MESSAGE"].format(pid)
				logger.warning(message)
				return jsonify({'result':[{"error":False, "message":message}]})
			else:
				res = r[0]
				# 删除path
				del res["path"]
				res["reverse_url"] = db.pixiv_re_proxy(res)
				_urls = json.loads(r["urls"].replace("'",'"'))
				r["reverse_url_api_original"] = _urls["original"].replace("i.pximg.net","i.pixiv.re")
				r["reverse_url_api_regular"] = _urls["regular"].replace("i.pximg.net","i.pixiv.re")
				res["error"],res["message"] = False,""
				logger.debug(res)
		except Exception as e:
			logger.warning("Exception: {}".format(e))
			message = TEMP_MSG["INTERNAL_ERROR_MESSAGE"].format("Exception", e)
			return jsonify({'result':[{"error":True, "message":message}]})
		else:
			logger.debug(f"<res> - {res}")
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
		# 是否开启R-18,默认开启
		is_r18 = request.form.get('is_r18',"True")
		# 指定数据表
		table = request.form.get('table',"bookmark")
		logger.info(f"Params | <num> - {num} | <ex> - {ex} | <limit> - {limit} |"\
					f" <illust_level> - {illust_level} | <is_r18> - {is_r18} | <table> - {table} |")

		# === num ===
		# num可转化为int类型
		try:
			int(num)
		except:
			message = TEMP_MSG["PARAM_ERROR"].format("num", num)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})
		# num <= 0
		if int(num) <= 0:
			message = TEMP_MSG["PARAM_ERROR"].format("num", num)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})
		# 大于单次返回最低限制
		if int(num) > RANDOM_LIMIT:
			logger.info(f"<num> - {num} greater than <RANDOM_LIMIT>")
			num = 1
		# === num ===

		# === limit ===
		# limit -> None 直接传参即可
		if limit:
			# limit可转化为int类型
			try:
				int(limit)
			except:
				message = TEMP_MSG["PARAM_ERROR"].format("limit", limit)
				logger.warning(message)
				return jsonify({'result':[{"error":True, "message":message}]})
			# limit <= 0
			if int(limit) <= 0:
				message = TEMP_MSG["PARAM_ERROR"].format("limit", limit)
				logger.warning(message)
				return jsonify({'result':[{"error":True, "message":message}]})
		# === limit ===

		# === extra ===
		if type(ex) != type("test") and ex:
			message = TEMP_MSG["PARAM_ERROR"].format("ex", ex)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})
		# === extra ===

		# === is_r18 ===
		is_r18_items = {"True":True, "False":False}
		if is_r18 not in list(is_r18_items.keys()):
			message = TEMP_MSG["PARAM_ERROR"].format("is_r18", is_r18)
			logger.warning(message)
			return jsonify({'result':[{"error":True, "message":message}]})
		else:
			is_r18 = is_r18_items[is_r18]
		# === is_r18 ===

		# 查询符合条件的所有pid_list
		result_pid_list = db.random_illust(extra=ex,limit=limit,
											illust_level=illust_level,
											is_r18=is_r18,table=table)

		logger.info(f"len result_pid_list - {len(result_pid_list)}")
		# 数据库查询无结果
		if result_pid_list == []:
			message = TEMP_MSG["NO_TAG_MESSAGE"]
			logger.warning(message)
			return jsonify({'result':[{"error":False, "message":message}]})

		# 数据库查询结果数量小于需求数量
		if len(result_pid_list) < int(num):
			random_pid_list = result_pid_list
		else:
			random_pid_list = random.sample(result_pid_list, int(num))

		res = []
		for _ in random_pid_list:
			r = db.select_illust(_["pid"],table=table)[0]
			# 删除path
			del r["path"]
			r["reverse_url"] = db.pixiv_re_proxy(r)
			_urls = json.loads(r["urls"].replace("'",'"'))
			r["reverse_url_api_original"] = _urls["original"].replace("i.pximg.net","i.pixiv.re")
			r["reverse_url_api_regular"] = _urls["regular"].replace("i.pximg.net","i.pixiv.re")
			r["error"],r["message"] = False,""
			res.append(r)

		res = [dict(t) for t in set([tuple(d.items()) for d in res])]
		logger.debug(f"<res> - {res} | <count> - {len(result_pid_list)}")
		return jsonify({'result':res, 'count':len(result_pid_list)})

# TODO 查询数据库数据表中是否有对应字段的记录
@app.route('/api/v2/check_item',methods=['GET','POST'])
def check_item():
	db = apier.db
	if request.method == "POST":
		key = request.form.get('key',"")
		value = request.form.get('value',"")
		table = request.form.get('table',"")
		database = request.form.get('database',None)

		try:
			result = db.check_illust(value,key,table,database)
		except Exception as e:
			result = [TEMP_MSG["API_ERROR"]]
		return jsonify({'result':[{"error":False, "message":result[0]}]})

# TODO 向数据库插入数据
@app.route('/api/v2/insert',methods=['GET','POST'])
def insert2db():
	pass

@app.errorhandler(404)
def error404(error):
	return jsonify({'result':[{"error":True, "message":TEMP_MSG["API_ADD_ERROR"]}]})

@app.errorhandler(500)
def error500(error):
	return jsonify({'result':[{"error":True, "message":TEMP_MSG["API_ERROR"]}]})


# if __name__ == '__main__':
	# app.debug = True
	# app.run(API_HOST,API_PORT)