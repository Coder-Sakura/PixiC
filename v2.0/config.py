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


# ================pixiv uid及cookie================
# pixiv uid用于获取用户的关注、收藏
# 一般是下载自己的pixiv关注和收藏,如需下载他人的
# 请填写他人的uid并选择另外的目录作为下载目录,避免存放到之前的目录中
USER_ID = ""


"""
设置该项以配置是否更新本地cookie  
首次运行请设置为True,后续运行可设置为False
"""
COOKIE_UPDATE_ENABLED = True
# COOKIE_UPDATE_ENABLED = False


"""
用于用户自定义cookie,
按照格式填写,将user_cookie替换为你复制的pixiv cookie
ORIGI_COOKIE_LIST = [
	'user_cookie',
]

1.注意!当自定义多个cookie时,请填写USER_ID字段.
2.目前自定义多cookie部分尚未完善,不填写USER_ID字段将
从定义的多个cookie中随机获取一个uid.
"""
ORIGI_COOKIE_LIST = []
# ================================================


# ======控制开关========
# 关注画师爬虫控制开关
PIXIV_CRAWLER_ENABLED = True

# 收藏作品爬虫控制开关
PIXIV_BOOKMARK_ENABLED = True

# API控制开关
# PIXIV_API_ENABLED = True
PIXIV_API_ENABLED = False
# ================================================


# ===============检测周期&最低限制=================
# 关注-画师作品检测周期,单位秒,默认43200秒,12小时
USERS_CYCLE = 43200

# 关注-最低收藏限制,高于LIMIT才会下载,默认3000
USERS_LIMIT = 3000

# 收藏-作品检测周期,单位秒,默认7200秒,2小时
BOOKMARK_CYCLE = 7200

# 收藏-最低收藏限制,高于LIMIT才会下载,默认为0
BOOKMARK_LIMIT = 0
# ================================================


# ==================API设置=======================
API_HOST = '0.0.0.0'
# 20200510 Pixiv网站排名 + 5
API_PORT = '1526'
# API数据库线程数
API_THREAD = 8
# API-random接口-最大返回数
RANDOM_LIMIT = 10
# API-random接口-返回数据收藏最低限制
# 默认不开启该功能,如需开启请移步db.random_illust
RANDOM_BOOKMARK_LIMIT = 3000
# ================================================


# ===============数据库连接信息====================
# 数据库开关,默认为关
# True则存储数据到数据库,不影响下载功能
# False时则不使用数据库,但同时部分API也无法使用
DB_ENABLE = True
# DB_ENABLE = False

# sql文件在doc目录下,为create.sql
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWD = '123456'
DB_DATABASE = 'moe'
DB_CHARSET = "utf8mb4"
# ================================================