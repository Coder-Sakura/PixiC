import pymysql
from DBUtils.PooledDB import PooledDB

from config import DB_HOST,DB_PORT,DB_USER,DB_PASSWD,DB_DATABASE,DB_CHARSET

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
# # maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
# DB_MAX_USAGE = 0
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

# 2019-11-24 05:56:33 表建好了,数据库模块写好了,后面用到接口的时候再接着谢了
class db_client(object):

	def __init__(self):
		self.pool = PooledDB(
		    pymysql,5,host=DB_HOST,user=DB_USER,
		    passwd=DB_PASSWD,db=DB_DATABASE,port=DB_PORT,charset=DB_CHARSET) # 5为连接池里的最少连接数
	
	def get_conn(self):
		conn = self.pool.connection() # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
		cur = conn.cursor()
		return conn,cur

	def insert(self,datas):
		"""
		需严格按照datas格式,否则后果自负
		:params datas:[(),()] or ((),())
		"""
		conn,cur = self.get_conn()

		sql = "INSERT INTO pra(name) VALUES(%s)"
		try:
			if len(datas) == 1:
				cur.execute(sql,datas)
			else:
				cur.executemany(sql,datas)
			conn.commit()
		except Exception as e:
			print(e)
			conn.rollback()
			return False
		finally:
			cur.close()
			conn.close()
			return True





"""
单例模式（Singleton Pattern）是一种常用的软件设计模式，该模式的主要目的是确保某一个类只有一个实例存在。
当你希望在整个系统中，某个类只能出现一个实例时，单例对象就能派上用场。

实例化一个对象时
是先执行了类的__new__方法（我们没写时，默认调用object.__new__）实例化对象
然后再执行类的__init__方法，对这个对象进行初始化，所有我们可以基于这个，实现单例模式


pixiv
多线程访问数据库连接池，池给一个连接，线程执行完sql后释放连接归还给连接池，此时

"""