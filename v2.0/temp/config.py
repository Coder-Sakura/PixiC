# coding=utf8
# ================================================
# 关注画师路径为空时,在脚本当前路径创建pixiv_crawler文件夹
# 示例,D:\pixiv_crawler
ROOT_PATH = r''

# 收藏作品路径为空时,在脚本当前路径创建bookmark文件夹
# 示例,D:\bookmark
BOOKMARK_PATH = r''

# Chrome浏览器用户数据目录
# 根据wiki进行更改,此为路径参考,一般只需要将<user>更改为你的用户名
# PRO_DIR = r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data'
PRO_DIR = r''
# ================================================


# ================账户uid及cookie================
# uid用于获取对应用户的关注、收藏作品
# 一般是下载自己的pixiv关注和收藏,如需下载他人的
# 请填写他人的uid并选择另外的目录作为下载目录,避免存放到之前的目录中
USER_ID = ""


"""
1. 设置该项以配置是否启动chrome浏览器更新本地cookie
2. 首次运行请设置为True,后续运行可设置为False
3. 该项设置为False及本地无cookie文件,会引发[Errno 2]异常
4. 若不想配置chrome可将此项设置为False,但要进行ORIGI_COOKIE_LIST的配置
"""
COOKIE_UPDATE_ENABLED = True
# COOKIE_UPDATE_ENABLED = False


"""
1. 自定义cookie,将user_cookie替换为你复制的pixiv cookie
2. 若有多个,则依次复制替换,注意结尾的','
ORIGI_COOKIE_LIST = [
	'user_cookie1',     
	'user_cookie2',
]

[WARNING]
1. 注意! 当自定义多个cookie时,请填写'USER_ID'字段
2. 否则将从指定的多个cookie中随机选取一个以获得对应的uid
3. 但这并不一定是你想要的uid,下载下来的关注作品和收藏作品
也不一定是你想要的
"""
ORIGI_COOKIE_LIST = []
# ================================================


# ======控制开关========
# 关注画师爬虫控制开关
PIXIV_CRAWLER_ENABLED = True

# 收藏作品爬虫控制开关
PIXIV_BOOKMARK_ENABLED = True

# API控制开关
PIXIV_API_ENABLED = False
# ================================================


# ===============检测周期&最低限制=================
# 关注-画师作品检测周期,单位秒,默认86400秒
USERS_CYCLE = 86400

# 关注-最低收藏限制,高于LIMIT才会下载,默认3000
# 若只想要数据库记录,可设置为99999
USERS_LIMIT = 3000

# 收藏-作品检测周期,单位秒,默认86400秒
BOOKMARK_CYCLE = 86400

# 收藏-最低收藏限制,高于LIMIT才会下载,默认为0
# 若只想要数据库记录,可设置为99999
BOOKMARK_LIMIT = 0
# ================================================


# ==================API设置=======================
API_HOST = '0.0.0.0'
# 2020/5/10 pixiv网站排名 + 5
API_PORT = '1526'
# API数据库线程数
API_THREAD = 8
# API-random接口-最大返回数
RANDOM_LIMIT = 10
# ================================================


# ===============数据库连接信息====================
# 数据库开关,默认为关
# True会存储数据到数据库
# False则不会存储数据,但同时部分API也无法使用
# DB_ENABLE = True
DB_ENABLE = False

# create.sql在doc目录下
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'pixiv'
DB_PASSWD = 'Huawei12#$'
DB_DATABASE = 'moe'
# 数据库/表的编码设置为utf8mb4  
# 插画信息中含emoji表情
DB_CHARSET = "utf8mb4"
# ================================================

# ===============DEBUG===============
DEBUG = False
# ===============DEBUG===============