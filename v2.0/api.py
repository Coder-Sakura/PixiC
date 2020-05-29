import os
import json
import time
from flask import Flask,request,jsonify

from config import API_HOST,API_PORT,RANDOM_LIMIT,API_THREAD
from downer import Downloader
from message import *


app = Flask(__name__)
db = Downloader.db

# 首页
@app.route('/api/v2')
def index():
	return "<h2>Now it's {} Welcome To PixiC API!</h2>".format(time.strftime("%Y-%m-%d %H:%M:%S"))

# 查询指定pid的信息
@app.route('/api/v2/get-info',methods=['GET','POST'])
def get_info():
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
			r = db.select_illust(pid)
			if r == "" or r == None:
				return jsonify({'result':[{"error":False,"message":NO_DATA_MESSAGE}]})
			else:
				r["reverse_url"] = db.pixiv_re_proxy(r)
				# 删除不必要的字段
				del r["urls"],r["path"]
				r["error"],r["message"] = False,""
				print("r",r)
		except Exception as e:
			print("e",e)
			return jsonify({'result':[{"error":True,"message":INTERNAL_ERROR_MESSAGE}]})
		else:
			res = [r]
			return jsonify({'result':res})

# 随机获取1~10条记录，最多指定2个tag
@app.route('/api/v2/random',methods=['GET','POST'])
def p_random():
	# extra指定tag
	if request.method == "POST":
		num = request.form.get('num',0)
		ex = request.form.get('extra',None)

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
		print("num",num,"tag",ex)

		res = []
		for i in range(int(num)):
			r = db.random_illust(extra=ex)
			if r == None:
				return jsonify({'result':{"error":False,"message":NO_TAG_MESSAGE}})
			r["reverse_url"] = db.pixiv_re_proxy(r)
			r["error"],r["message"] = False,""
			res.append(r)
		print(res)
		return jsonify({'result':res})

# 调用则向数据库插入数据
@app.route('/api/v2/i-db',methods=['GET','POST'])
def insert2db():
	pass

@app.errorhandler(404)
def error404(error):
	return API_ADD_ERROR

@app.errorhandler(500)
def error500(error):
	return API_ERROR

if __name__ == '__main__':
	# 通过设置app.run()的参数，来达到多线程的效果
	# threaded True开启,默认为False
	# processes True开启,默认是False,开启默认是一个进程
	# 建议flask开启多线程处理并发,通过 UWSGI/Gunicorn 之类的调度器去控制并发数量
	# app.debug = True
	app.run(API_HOST,API_PORT)