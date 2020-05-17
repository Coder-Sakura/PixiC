# coding=utf8
import random
import pymysql
from DBUtils.PooledDB import PooledDB
# fetchall结果转字典
from pymysql.cursors import DictCursor

from config import DB_HOST,DB_PORT,DB_USER,DB_PASSWD,DB_DATABASE,DB_CHARSET,RANDOM_BOOKMARK_ENABLE,RANDOM_BOOKMARK_LIMIT
from logstr import log_str



# 2019-11-24 05:56:33
# 2020-04-22
class db_client(object):
	"""
	关注画师-数据库流程:
		1. check_user 查询pxusers表中是否含该画师id字段信息
			有,返回数据库中该画师的最新插画id
			无,创建该画师记录
		2. get_total 查询pixiv表中有多少表该画师id字段信息
		3. update_latest_id 符合更新条件,更新pxusers表中该画师id的最新插画id
		4. 队列中,check_illust 查询pixiv表中是否有该pid的记录
		5. 队列中,updata_illust 每次作品网络请求,都会进行该pid数据的更新
		6. 队列中,insert_illust 满足插入条件,向pixiv表中插入该pid的记录

	收藏作品-数据库流程:
		1. 判断更新条件
		2. 队列中,check_illust 查询pixiv表中是否有该pid的记录
		3. 队列中,updata_illust 每次作品网络请求,都会进行该pid数据的更新
		4. 队列中,insert_illust 满足插入条件,向pixiv表中插入该pid的记录
	"""

	def __init__(self):
		pass
		log_str("数据库连接池实例化...")
		# self.create_db if flag == True
	
	def create_db(self,thread_num=16):
		"""
		:params thread_num: 数据库连接池线程数
		"""
		try:
			self.pool = PooledDB(
			    pymysql,thread_num,host=DB_HOST,user=DB_USER,
			    passwd=DB_PASSWD,db=DB_DATABASE,port=DB_PORT,charset=DB_CHARSET) # 5为连接池里的最少连接数
		except pymysql.err.OperationalError as e:
			log_str("请确保Mysql在运行/配置好\n{}".format(e))
			exit()
		log_str("数据库连接池完成...")

	def get_conn(self):
		"""
		DictCursor 返回结果由元组类型转为字典类型
		res = function()
		res[0][select_name]
		"""
		conn = self.pool.connection() # 以后每次需要数据库连接就是用connection()函数获取连接就好了
		cur = conn.cursor(DictCursor)
		return conn,cur

	def check_user(self,u):
		"""
		数据库中画师记录的latest_id与接口返回的latest_id是否一致
		相同 --> False,不需要下载该画师

		判断pxusers表是否含有该画师信息
		无 --> 插入数据
		有 --> null
		:return: latest_id
		出现mysql 1366报错,按照https://blog.csdn.net/qq_31122833/article/details/83992085解决
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
		# 更新latest_id sql

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
				print(e)
				conn.rollback()
				# 默认全更新
				# return False
				return u["latest_id"]
			else:
				return u["latest_id"]
			finally:
				cur.close()
				conn.close()

	def get_total(self,u):
		"""
		查询数据库中有多少条[画师uid]的数据
		:params u: 作品数据
		:return: d_total
		"""
		conn,cur = self.get_conn()
		sql = '''SELECT COUNT(*) FROM pixiv WHERE uid=%s'''
		data = u["uid"]
		cur.execute(sql,data)
		d = cur.fetchall()[0]
		d_total = d["COUNT(*)"]
		return d_total

	def update_latest_id(self,u):
		"""
		更新latest_id
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
			prnit(e)
			conn.rollback()
		finally:
			cur.close()
			conn.close()

	def check_illust(self,pid,table="pixiv"):
		"""
		查询数据库中是否有该id的作品
		:return : 是否存在该记录,path
		path为下载地址,不存在该记录时为None
		"""
		conn,cur = self.get_conn()
		# 查询id sql
		sql = """SELECT COUNT(*),path FROM {} """.format(table) + """WHERE pid=%s"""
		data = (pid)
		cur.execute(sql,data)
		d = cur.fetchall()[0]
		if d["COUNT(*)"] >= 1:
			return True,d["path"]
		else:
			# if d["path"] == None:
			# 	print("is None")
			return False,d["path"]

	def insert_illust(self,u,table="pixiv"):
		"""
		data格式:{key:value,...}
		:params datas 数据
		出现mysql 1366报错,按照https://blog.csdn.net/qq_31122833/article/details/83992085解决
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
			# if len(data) == 1:
			# 	cur.execute(sql,data)
			# else:
			# 	cur.executemany(sql,data)
			conn.commit()
		except Exception as e:
			print(e)
			log_str(u)
			conn.rollback()
			return False
		else:
			return True
		finally:
			cur.close()
			conn.close()

	def updata_illust(self,u,table="pixiv"):
		"""
		更新作品数据,主要是浏览数,收藏数,评论数,喜欢数
		:params u:作品数据
		:return :
		主要更新 viewCount bookmarkCount commentCount likeCount
		"""
		conn,cur = self.get_conn()
		# 更新sql
		# 更新前 72 32 23 0 81265370
		# 更新后 1  1  1  1 81265370
		# 快速查询 SELECT viewCount,bookmarkCount,likeCount,commentCount,pid FROM pixiv WHERE id=53312;
		sql = """UPDATE {} """.format(table) + """SET viewCount=%s,\
				bookmarkCount=%s,likeCount=%s,commentCount=%s WHERE pid=%s"""
		# 更新数据
		data = (
			u["viewCount"],u["bookmarkCount"],u["likeCount"],u["commentCount"],u["pid"]
			)
		try:
			cur.execute(sql,data)
			conn.commit()
		except Exception as e:
			log_str(e)
			log_str(u)
			conn.rollback()
			return False
		else:
			return True
		finally:
			cur.close()
			conn.close()

	def select_illust(self,pid,table="pixiv"):
		"""
		查询作品数据
		"""
		conn,cur = self.get_conn()
		sql = """SELECT * FROM {} """.format(table) + """WHERE pid=%s"""
		data = (pid,)
		cur.execute(sql,data)
		r = cur.fetchall()
		if len(r) != 0:
			# print(r)
			res = r[0]
			return res
		else:
			return

	def random_illust(self,table="pixiv",extra=None):
		"""
		:params table: 指定哪个表
		:params extra: ["原创","碧蓝航线"] 最多2个,额外指定tag
		随机返回1条数据,根据extra返回对应的标签
		不返回urls,path,t2.id等非必要字段或中间产物
		"""
		conn,cur = self.get_conn()
		sql = """\
		SELECT * FROM {} AS t1 """.format(table) + \
		"""JOIN (SELECT ROUND(RAND() * ((SELECT MAX(id) FROM {})-""".format(table) + \
		"""(SELECT MIN(id) FROM {}))+""".format(table) + \
		"""(SELECT MIN(id) FROM {})) AS id) AS t2 """.format(table) + \
		"""WHERE t1.id >= t2.id \
		"""
		e = """AND tag LIKE "%{}%" """
		# 默认是取收藏大于3000的
		b = " "
		if RANDOM_BOOKMARK_ENABLE:
			b = """AND bookmarkCount > {} """.format(RANDOM_BOOKMARK_LIMIT)
		limit = """ORDER BY t1.id LIMIT 1"""

		if extra:
			ex = extra.split(",")[:2]
			for i in ex:
				sql = sql + e.format(i)
		s = sql + b + limit
		cur.execute(s)
		r = cur.fetchall()
		if len(r) == 0:
			return None
		else:
			del r[0]["urls"],r[0]["path"],r[0]["t2.id"]
			return r[0]

	def pixiv_re_proxy(self,u):
		"""
		根据作品数据反代
		动图单图:pixiv.cat/{id}.{Suffix}
		多图:pixiv.cat/{id}-{num}.{Suffix}
		"""
		h = "https://pixiv.cat/"
		pid = u["pid"]
		suffix = u["original"].split(".")[-1]
		if u["pageCount"] > 1:
			num = random.randint(1,u["pageCount"])
			reverse_url = "{}{}-{}.{}".format(h,pid,num,suffix)
		else:
			reverse_url = "{}{}.{}".format(h,pid,suffix)
		return reverse_url



DBclient = db_client()





"""
单例模式（Singleton Pattern）是一种常用的软件设计模式，该模式的主要目的是确保某一个类只有一个实例存在。
当你希望在整个系统中，某个类只能出现一个实例时，单例对象就能派上用场。

实例化一个对象时
是先执行了类的__new__方法（我们没写时，默认调用object.__new__）实例化对象
然后再执行类的__init__方法，对这个对象进行初始化，所有我们可以基于这个，实现单例模式


pixiv
多线程访问数据库连接池，池给一个连接，线程执行完sql后释放连接归还给连接池，此时
	
pymysql用%s指定表名,pymysql会自动转义含%s的字符串,所以%s指定表名会出现1064报错
解决:
sql = 'insert into %s(name,age)' %TabName + ' value (%s)'
cursor.execute(sql, [name])
目前：
sql = SELECT COUNT(*),path FROM {} .format(table) + WHERE pid=%s"

"""

# # 数据库连接编码
# DB_CHARSET = "utf8"
# # mincached : 启动时开启的闲置连接数量(缺省值 0 开始时不创建连接)
# DB_MIN_CACHED = 10
# # maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
# DB_MAX_CACHED = 10
# # maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
# DB_MAX_SHARED = 20
# # maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
# DB_MAX_CONNECYIONS = 100
# # blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......> 其他代表阻塞直到连接数减少,连接被分配)
# DB_BLOCKING = True
# # maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,# DB_MAX_USAGE = 0
# # setsession : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
# DB_SET_SESSION = None
# # creator : 使用连接数据库的模块
# DB_CREATOR = pymysql

"""
为什么mysql有些表需要提交事务有些不需要呢？
1.首先得看mysql支持的存储引擎
查看表使用的存储引擎：show create table pra;

查看mysql支持的存储引擎：show engines \G;

innodb是支持事务的引擎,如果没有开启自动提交事务(commit)，则需要手动提交.
myisam是不支持事务的引擎,是否提交事务(commit)都是无效的.

目前大量的update和insert，建议使用InnoDB，特别是针对多个并发和QPS(每秒查询率)较高的情况。
"""