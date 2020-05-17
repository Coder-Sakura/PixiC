import os
import json
from flask import Flask,request,jsonify

from downer import Downloader
from config import API_HOST,API_PORT,RANDOM_LIMIT,API_THREAD


app = Flask(__name__)

db = Downloader.db
# db.create_db(thread_num=API_THREAD)

# 查询不到数据
NO_DATA_MESSAGE = "There Is No Data Corresponding To This Pid"
# 没有该标签的作品
NO_TAG_MESSAGE = "There Is No Illusts Corresponding To The Tag"
# 内部错误
INTERNAL_ERROR_MESSAGE = "Internal Error"


# 首页
@app.route('/api/v2')
def index():
	return "<h2>Welcome To PixivCrawler API!</h2>"

# 查询指定pid的信息
@app.route('/api/v2/get-info',methods=['GET','POST'])
def get_info():
	if request.method == "POST":
		pid = request.form.get('pid',None)
		if pid == None or len(pid) > 20:
			return jsonify({'result':{"error":False,"message":NO_DATA_MESSAGE}})
		try:
			res = db.select_illust(pid)
			res["reverse_url"] = db.pixiv_re_proxy(res)
			print("res",res)
			if res == "" or res == None:
				res = {"error":False,"message":NO_DATA_MESSAGE}
			else:
				# 删除不必要的字段
				del res["urls"],res["path"]
				res["error"],res["message"] = False,""
		except Exception as e:
			res = {"error":True,"message":INTERNAL_ERROR_MESSAGE}
		finally:	
			return jsonify({'result':res})

# 随机获取1~10条记录，最多指定2个tag
@app.route('/api/v2/random',methods=['GET','POST'])
def p_random():
	# extra指定tag
	# 单tag: ta .method == "POST":
	if request.method == "POST":
		num = int(request.form.get('num',1))
		ex = request.form.get('extra',None)

		if num > RANDOM_LIMIT:
			num = 1
		print(num,ex)
		res = []
		for i in range(num):
			r = db.random_illust(extra=ex)
			r["reverse_url"] = db.pixiv_re_proxy(r)
			if r == None:
				return jsonify({'result':{"error":False,"message":NO_TAG_MESSAGE}})
			res.append(r)
		return jsonify({'result':res})

# 调用则向数据库插入数据
@app.route('/api/v2/i-db',methods=['GET','POST'])
def insert2db():
	pass

@app.errorhandler(404)
def error404(error):
	return "请检查API地址!"

@app.errorhandler(500)
def error500(error):
	return "出错了"

if __name__ == '__main__':
	# 通过设置app.run()的参数，来达到多线程的效果
	# threaded True开启,默认为False
	# processes True开启,默认是False,开启默认是一个进程
	# 建议flask开启多线程处理并发,通过 UWSGI/Gunicorn 之类的调度器去控制并发数量
	# app.debug = True
	app.run(API_HOST,API_PORT)