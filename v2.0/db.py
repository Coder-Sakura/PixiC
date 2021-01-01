# coding=utf8
import os
import random
import pymysql
from DBUtils.PooledDB import PooledDB
# DictCursor 使返回结果由元组类型转为字典类型
from pymysql.cursors import DictCursor

from config import *
from logstr import log_str
from message import *


class db_client(object):
	"""
	关注画师-数据库流程:
		1. check_user 查询pxusers表中是否含该画师id字段信息
			有,返回数据库中该画师的最新插画id
			无,创建该画师记录
		2. get_total 查询pixiv表中有多少表该画师id字段信息
		3. update_latest_id 符合更新条件,更新pxusers表中该画师id的最新插画id
		4. 队列中,check_illust 查询pixiv表中是否有该pid的记录
		5. 队列中,update_illust 每次作品网络请求,都会进行该pid数据的更新
		6. 队列中,insert_illust 满足插入条件,向pixiv表中插入该pid的记录

	收藏作品-数据库流程:
		1. 判断更新条件
		2. 队列中,check_illust 查询pixiv表中是否有该pid的记录
		3. 队列中,update_illust 每次作品网络请求,都会进行该pid数据的更新
		4. 队列中,insert_illust 满足插入条件,向pixiv表中插入该pid的记录
	"""

	def __init__(self, thread_num=8):
		self.class_name = self.__class__.__name__
		if DB_ENABLE == False:
			return

		log_str(DB_INST.format(self.__class__.__name__))
		try:
			self.pool = PooledDB(		
			    creator=pymysql,
			    maxconnections=thread_num,	# 连接池允许的最大连接
			    mincached=1,	# 连接池中的初始空闲连接数
			    maxcached=1,	# 连接池中最大闲置连接数
			    host=DB_HOST,user=DB_USER,passwd=DB_PASSWD,db=DB_DATABASE,port=DB_PORT,charset=DB_CHARSET
			)
		except pymysql.err.OperationalError as e:
			log_str(DB_CONNECT_ERROR_INFO.format(e))
			exit()

	def get_conn(self):
		"""
		从数据库连接池中取出一个链接
		"""
		# connection()获取数据库连接
		conn = self.pool.connection() 
		cur = conn.cursor(DictCursor)
		return conn,cur

	def check_user(self, u):
		"""
		数据库中画师记录的latest_id与接口返回的latest_id是否一致
		相同 --> False,不需要下载该画师

		判断pxusers表是否含有该画师信息
		无 --> 插入数据
		有 --> null

		:params u: 用户数据
		:return: latest_id
		"""
		conn,cur = self.get_conn()
		# 查询画师记录sql
		sql_1 = "SELECT COUNT(uid) FROM pxusers WHERE uid=%s"
		# 插入画师记录sql
		sql_2 = '''INSERT INTO pxusers(uid,userName,latest_id,path) VALUES(%s,%s,%s,%s)'''
		# 查询latest_id sql
		sql_3 = "SELECT latest_id FROM pxusers WHERE uid=%s"

		uid = u["uid"]
		data = (
			u["uid"],u["userName"],u["latest_id"],u["path"]
				)

		# 确认数据库是否有该画师记录
		cur.execute(sql_1,uid)
		res = cur.fetchall()
		e = res[0]["COUNT(uid)"]
		# log_str("查询结果 :{}".format(e))

		if e >= 1:
			# 返回数据库中查询的latest_id
			cur.execute(sql_3,uid)
			d = cur.fetchall()[0]
			latest_id = d["latest_id"]
			return latest_id
		else:
			try:
				cur.execute(sql_2,data)
				conn.commit()
			except Exception as e:
				log_str(e)
				conn.rollback()
				# 默认全更新
				return u["latest_id"]
			else:
				return u["latest_id"]
			finally:
				cur.close()
				conn.close()

	def get_total(self, u):
		"""
		查询数据库中有多少条[画师uid]的数据
		:params u: 作品数据
		:return: 画师作品数量
		"""
		conn,cur = self.get_conn()
		sql = '''SELECT COUNT(1) FROM pixiv WHERE uid=%s'''
		data = u["uid"]
		cur.execute(sql,data)
		d = cur.fetchall()[0]
		# d_total = d["COUNT(*)"]
		d_total = d["COUNT(1)"]
		return d_total

	def update_latest_id(self, u):
		"""
		更新latest_id
		:params u: 作品数据
		:return:
		"""
		conn,cur = self.get_conn()
		# 更新latest	_id sql
		sql = """UPDATE pxusers SET latest_id=%s WHERE uid=%s"""
		data = (
			u["latest_id"],u["uid"]
				)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			log_str(e)
			conn.rollback()
		finally:
			cur.close()
			conn.close()

	def check_illust(self, value, key="pid", table="pixiv", database=None):
		"""
		查询数据库中是否有该id的作品,table为非pixiv,bookmark时采用通用sql		
		:parmas key: 对应字段名
		:parmas value: 对应记录值
		:parmas table: 数据表
		:return: (True,path)/(False,"")
		Result--fetchall
			data in db: [{'COUNT(1)': 1, 'path': 'None'}]
			data not in db: ()
		"""
		conn,cur = self.get_conn()
		if key == "":
			return False,""

		if value == "":
			return False,""

		# 切换数据库
		if database != None:
			conn.select_db(database)

		# 查询id sql
		if table in ["pixiv","bookmark"]:
			# path为下载地址,不存在该记录时为None
			sql = """SELECT COUNT(1),path FROM {} """.format(table) + """WHERE {}=%s GROUP BY path""".format(key)
		else:
			sql = """SELECT COUNT(1) FROM {} """.format(table) + """WHERE {}=%s""".format(key)
		# log_str(sql)
		data = (value)
		try:
			cur.execute(sql,data)
		except Exception as e:
			log_str("{}:check_illust | {}".format(self.class_name),e)
			return False,""
		else:
			# 未使用GROUP BY path,非严格模式报1140
			# 使用GROUP BY path,不存在对应pid记录时,fetchall结果为()
			d = cur.fetchall()
			if d != () and d[0]["COUNT(1)"] >= 1:
				return True,d[0].get("path","")
			else:
				return False,""
		finally:
			cur.close()
			conn.close()

	def insert_illust(self, u, table="pixiv"):
		"""
		:params u 数据
		:parmas table: 操作数据表
		:return: True/False
		"""
		conn,cur = self.get_conn()

		sql = '''INSERT INTO {} '''.format(table) + '''(uid,userName,pid,purl,title,tag,pageCount,\
						illustType,is_r18,viewCount,bookmarkCount,likeCount,\
						commentCount,urls,original,path) VALUES(%s,%s,%s,%s,\
						%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
		data = (
			u["uid"],u["userName"],u["pid"],u["purl"],u["title"],u["tag"],
			u["pageCount"],u["illustType"],u["is_r18"],u["viewCount"],
			u["bookmarkCount"],u["likeCount"],u["commentCount"],u["urls"],
			u["original"],u["path"]
				)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			log_str(e)
			# log_str(u)
			conn.rollback()
			return False
		else:
			return True
		finally:
			cur.close()
			conn.close()

	def update_illust(self, u, table="pixiv"):
		"""
		更新作品数据,主要是浏览数,收藏数,评论数,喜欢数,path
		:params u:作品数据
		:parmas table: 操作数据表
		:return :
		主要更新 viewCount bookmarkCount commentCount likeCount
		"""
		conn,cur = self.get_conn()

		# 更新前 72 32 23 0 81265370
		# 更新后 1  1  1  1 81265370
		# 快速查询 SELECT viewCount,bookmarkCount,likeCount,commentCount,pid FROM pixiv WHERE id=53312;
		# 更新sql
		sql = """UPDATE {} """.format(table) + """SET viewCount=%s,\
				bookmarkCount=%s,likeCount=%s,commentCount=%s,path=%s WHERE pid=%s"""
		# 更新数据
		data = (
			u["viewCount"],u["bookmarkCount"],u["likeCount"],u["commentCount"],u["path"],u["pid"]
			)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			log_str(DB_UPDATE_ILLUST_ERROR_INF.format(self.class_name,u["pid"],e))
			conn.rollback()
			return False
		else:
			return True
		finally:
			cur.close()
			conn.close()

	def select_illust(self, pid, table="pixiv"):
		"""
		查询作品数据,对接API接口方法
		:params pid:作品pid
		:parmas table: 操作数据表
		:return :
		"""
		conn,cur = self.get_conn()
		sql = """SELECT * FROM {} """.format(table) + """WHERE pid=%s"""
		data = (pid,)
		try:
			cur.execute(sql,data)
		except Exception as e:
			log_str(e)
			return
		else:
			r = cur.fetchall()
			if len(r) != 0:
				# API处增加[0]下标
				# res = r[0]
				return r
			else:
				return
		finally:
			cur.close()
			conn.close()

	def random_illust(self,
			extra=None, 
			table="pixiv", 
			random_bookmark_enable=False
		):
		"""
		对接API-p_random接口
		:params extra: tag组 原创,碧蓝航线
		:parmas table: 数据表
		:params random_bookmark_enable: 
		是否返回小于RANDOM_BOOKMARK_LIMIT收藏数的作品

		返回符合条件的所有数据
		删除urls,path,t2.id等非必要字段/中间字段
		"""
		conn,cur = self.get_conn()
		sql = """SELECT pid FROM {} WHERE 1 = 1 """.format(table)
		# tag搜索
		e = """AND tag LIKE "%{}%" """
		
		if extra:
			ex = extra.split(",")[:2]
			for i in ex:
				sql = sql + e.format(i)

		# 默认关闭取收藏大于3000
		if random_bookmark_enable:
			b = """AND bookmarkCount > {} """.format(RANDOM_BOOKMARK_LIMIT)
			sql += b

		cur.execute(sql)
		pid_list = cur.fetchall()
		if len(pid_list) == 0:
			return []
		else:
			return pid_list

	def pixiv_re_proxy(self, u):
		"""
		根据作品数据反代
		动图单图:pixiv.cat/{id}.{Suffix}
		多图:pixiv.cat/{id}-{num}.{Suffix}

		:params u:作品数据
		:returnL 反代链接
		"""
		h = "https://pixiv.cat/"
		pid = u["pid"]
		suffix = u["original"].split(".")[-1]
		if u["pageCount"] > 1:
			num = random.randint(1,u["pageCount"])
			reverse_url = "{}{}-{}.{}".format(h,pid,num,suffix)
			# reverse_url = u["original"].replace(d,h)
		else:
			reverse_url = "{}{}.{}".format(h,pid,suffix)
			# reverse_url = u["original"].replace(d,h)
		return reverse_url

	# TODO
	def insert2suolink(self, data, table="suolink", database=None):
		pass


# DBClient = db_client()