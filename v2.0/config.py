# coding=utf8
# ================================================
# 关注画师路径为空时,在脚本当前路径创建pixiv_crawler文件夹
ROOT_PATH = r''

# 收藏作品路径为空时,在脚本当前路径创建bookmark文件夹
BOOKMARK_PATH = r''

# Chrome用户数据目录
PRO_DIR = r''
# 根据wiki进行更改,此为路径参考,一般只需更改用户名
# PRO_DIR = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'
# ================================================


# ================账户uid及cookie================
# uid用于获取登录用户的关注画师、收藏  
# 不知道的话留空,请不要随意填写
USER_ID = ""

# 设置该项以配置是否更新本地cookie  
# 首次运行请设置为True
# 后续运行可设置为False,但请保证本地的cookie文件与COOKIE_NAME一致
# 该项设置为False及本地无cookie文件,会引发[Errno 2]异常
# COOKIE_UPDATE_ENABLED = True
COOKIE_UPDATE_ENABLED = False
# ================================================


# ======控制开关========
# 关注画师爬虫控制开关
PIXIV_CRAWLER_ENABLED = True

# 收藏作品爬虫控制开关
PIXIV_BOOKMARK_ENABLED = True

# Api控制开关
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
# 端口
API_PORT = '1526'
# API数据库线程数
API_THREAD = 8
# API-random接口-最大返回数
RANDOM_LIMIT = 10
# API-random接口-是否开启收藏数筛选
RANDOM_BOOKMARK_ENABLE = True
# API-random接口-返回插画最小收藏数
RANDOM_BOOKMARK_LIMIT = 3000
# ================================================


# ===============数据库连接信息====================
# 数据库开关.为True则存储数据到数据库
# False时则根据筛选条件直接下载原图,但同时API也无法使用
# 默认不使用
# DB_ENABLE = True
DB_ENABLE = False

# sql文件在doc目录下,为create.sql
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWD = '123456'
DB_DATABASE = 'moe'
# 建议数据库和表都设置为utf8mb4  
# 插画信息中含有emoji表情
DB_CHARSET = "utf8mb4"
# ================================================