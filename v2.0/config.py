# coding=utf8

# import hashlib
# h = hashlib.md5()
# h.update(bytes(__file__,encoding='utf-8'))
# COOKIE_NAME = h.hexdigest()
# print(COOKIE_NAME)
# 加密txt

# ================================================
# 关注画师路径为None时,在脚本当前路径创建pixiv_crawler文件夹
ROOT_PATH = r'H:\se18'
# ROOT_PATH = None

# 收藏作品路径为None时,在脚本当前路径创建bookmark文件夹
BOOKMARK_PATH = r'H:\bookmark'
# Chrome用户数据目录
PRO_DIR = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'
# ================================================


# ================================================
# 登录用户的uid,如果知道的话,填入可以加速启动
# uid用于获取登录用户的关注画师及收藏作品
# 如果不知,请不要随意改动,等待脚本获取
USER_ID = "27858363"
# USER_ID = ""

# 存储Cookie的文件名
COOKIE_NAME = 'pixiv_cookie'

# 首次运行请设置'COOKIE_UPDATE_ENABLED'为True以更新Cookie
# 后续运行可以设置'COOKIE_UPDATE_ENABLED'为False以直接获取缓存下来的Cookie
# 不过请注意,Pixiv的Cookie有效时间虽长,但每隔一段时间仍需要设置'COOKIE_UPDATE_ENABLED'以更新过期Cookie
# COOKIE_UPDATE_ENABLED = True
COOKIE_UPDATE_ENABLED = False
# ================================================


# ======控制开关========
# 关注画师爬虫控制开关
PIXIV_CRAWLER_ENABLED = False
# 收藏作品爬虫控制开关
PIXIV_BOOKMARK_ENABLED = True
# api控制开关
PIXIV_API_ENABLED = False
# ================================================


# ================================================
# 检测周期&最低限制
# 关注-画师作品检测周期,单位秒,默认600秒
# USERS_CYCLE = 600
USERS_CYCLE = 1800
# 关注-最低收藏限制,高于LIMIT才会下载,默认3000
USERS_LIMIT = 3000
# 收藏-作品检测周期,单位秒,默认1800秒
BOOKMARK_CYCLE = 300
# BOOKMARK_CYCLE = 1800
# 收藏-最低收藏限制,高于LIMIT才会下载,默认为0
BOOKMARK_LIMIT = 0
# ================================================


# ================================================
# API设置
# 主机
API_HOST = '0.0.0.0'
# 端口
# 20200510 pixiv 网站排名 + 5
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




# ===数据库连接信息======
DB_HOST = 'localhost'	# 127.0.0.1
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWD = '123456'
# 收藏、关注的数据都放在这个数据库
DB_DATABASE = 'moe'
DB_CHARSET = "utf8"
# =====================
