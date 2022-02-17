# coding=utf8
import os
import random
import pymysql
from DBUtils.PooledDB import PooledDB
# DictCursor 使返回结果由元组类型转为字典类型
from pymysql.cursors import DictCursor

# from config import *
from config import DB_ENABLE,DB_HOST,DB_USER,\
	DB_PASSWD,DB_DATABASE,DB_PORT,DB_CHARSET
from log_record import logger
from message import TEMP_MSG


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

	def __init__(self, thread_num=16):
		self.class_name = self.__class__.__name__
		if DB_ENABLE == False:
			return

		logger.info(TEMP_MSG["DB_INST"].format(self.class_name))
		try:
			self.pool = PooledDB(		
			    creator=pymysql,
			    maxconnections=thread_num,	# 连接池允许的最大连接
			    mincached=1,	# 连接池中的初始空闲连接数
			    maxcached=1,	# 连接池中最大闲置连接数
				# 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
				blocking=True,
			    host=DB_HOST,user=DB_USER,passwd=DB_PASSWD,db=DB_DATABASE,port=DB_PORT,charset=DB_CHARSET
			)
		except pymysql.err.OperationalError as e:
			logger.warning(TEMP_MSG["DB_CONNECT_ERROR_INFO"].format(e))
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
		相同 --> False,不需要更新或下载该画师的作品

		判断pxusers表是否含有该画师uid的记录
		无 --> sql_2
		有 --> sql_3

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
		# logger.debug("查询结果 :{}".format(e))

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
				logger.warning(f"<Exception> - {e}")
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
			logger.warning("{} | {}".format(e,u))
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
		Result--fetchall获取的原始数据
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
		# logger.debug(sql)
		data = (value)
		try:
			cur.execute(sql,data)
		except Exception as e:
			logger.warning("{}:check_illust | {}".format(self.class_name,e))
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
						illustType,is_r18,score,illust_level,viewCount,bookmarkCount,likeCount,\
						commentCount,urls,original,path) VALUES(%s,%s,%s,%s,\
						%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
		data = (
			u["uid"],u["userName"],u["pid"],u["purl"],u["title"],u["tag"],
			u["pageCount"],u["illustType"],u["is_r18"],u["score"],u["illust_level"],
			u["viewCount"],u["bookmarkCount"],u["likeCount"],u["commentCount"],
			u["urls"],u["original"],u["path"]
				)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			logger.warning("{} | {}".format(e,u))
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
		:return: True/False
		更新11个字段 tag,pageCount,illustType,is_r18,score,illust_level,
				viewCount,bookmarkCount,likeCount,commentCount,path
		"""
		conn,cur = self.get_conn()

		# 更新sql
		sql = """UPDATE {} """.format(table) + """SET tag=%s,pageCount=%s,\
				illustType=%s,is_r18=%s,score=%s,illust_level=%s,viewCount=%s,\
				bookmarkCount=%s,likeCount=%s,commentCount=%s,path=%s WHERE pid=%s"""
		# 更新数据
		data = (
			u["tag"],u["pageCount"],u["illustType"],u["is_r18"],u["score"],u["illust_level"],
			u["viewCount"],u["bookmarkCount"],u["likeCount"],u["commentCount"],u["path"],u["pid"]
		)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			logger.warning(TEMP_MSG["DB_UPDATE_ILLUST_ERROR_INFO"].format(self.class_name,u["pid"],e))
			logger.warning(f"illust_data - {u}")
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
			logger.warning(f"<Exception> - {e}")
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
			limit=None,
			illust_level=None,
			is_r18=True,
			table="pixiv"
		):
		"""
		对接API-random接口
		:params extra: 指定tag组(str),如原创,碧蓝航线;最多两个
		:params limit: 指定最低收藏数(str),
		:params illust_level: 指定单个或多个评分等级(str) str;如:SR或R,SR,SSR,UR
		:params is_r18: 是否开启R18;
			默认True开启,False为关闭,关闭则会过滤掉tag中包含'R-18'的结果
		:parmas table: 数据表

		返回符合条件的所有pid
		删除urls,path,t2.id等非必要字段/中间字段
		"""
		conn,cur = self.get_conn()
		sql = """SELECT pid FROM {} WHERE 1 = 1 """.format(table)
		
		# 指定tag
		e = """AND tag LIKE "%{}%" """		
		if extra:
			ex = extra.split(",")[:2]
			for i in ex:
				sql = sql + e.format(i)

		# 指定最低收藏数限制
		if limit:
			limit_sql = """AND bookmarkCount > {} """.format(str(limit))
			sql += limit_sql

		# 指定评分等级
		if illust_level:
			illust_level = ",".join(["'{}'".format(_) for _ in illust_level.split(",")])
			illust_level_sql = """AND illust_level in ({}) """.format(str(illust_level))
			sql += illust_level_sql

		# 关闭r18
		if not is_r18:
			is_r18_sql = """AND tag NOT LIKE "%R-18%" """
			sql += is_r18_sql

		logger.debug(sql)
		cur.execute(sql)
		pid_list = cur.fetchall()
		if len(pid_list) == 0:
			return []
		else:
			return pid_list

	def delete_user_illust(self, key="uid", value=None, table="pixiv"):
		"""
		删除指定user的所有/单条作品记录

		:params key: 用于判断的key,默认为uid
		:params value: 用于判断的值
		:params table: 指定数据表,默认为pixiv
		:return: 默认None,异常则False
		"""			
		if value == None:
			return False

		conn,cur = self.get_conn()
		sql = """DELETE FROM {} WHERE {} = %s""".format(table,str(key))

		data = (value,)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			logger.warning("{} | {}".format(e,(key,value)))
			conn.rollback()
			return False
		else:
			return True
		finally:
			cur.close()
			conn.close()

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
			# 暂时为1
			num = 1
			reverse_url = "{}{}-{}.{}".format(h,pid,num,suffix)
		else:
			reverse_url = "{}{}.{}".format(h,pid,suffix)
		return reverse_url

# DBClient = db_client()