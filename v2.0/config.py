# coding=utf8
# ================================================
# 关注画师路径为None时,在脚本当前路径创建pixiv_crawler文件夹
ROOT_PATH = r'H:\se18'
# ROOT_PATH = None

# 收藏作品路径为None时,在脚本当前路径创建bookmark文件夹
BOOKMARK_PATH = r'H:\bookmark'

# Chrome用户数据目录
PRO_DIR = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'
# ================================================


# ================账户uid及cookie================
# uid用于获取登录用户的关注画师、收藏  
# 不知道的话留空,请不要随意填写
USER_ID = "27858363"
# USER_ID = ""

# 存储用户cookie的文件名称
COOKIE_NAME = 'pixiv_cookie'

# 是否更新本地cookie  
# 首次运行请设置为True以创建你的cookie  
# 后续运行可以设置为False以直接使用之前持久化下来的Cookie  
# 注意!!cookie存在时效,启动爬虫前,先用chrome访问pixiv试试  
# COOKIE_UPDATE_ENABLED = True
COOKIE_UPDATE_ENABLED = False
# ================================================


# ======控制开关========
# 关注画师爬虫控制开关
PIXIV_CRAWLER_ENABLED = True

# 收藏作品爬虫控制开关
PIXIV_BOOKMARK_ENABLED = False

# Api控制开关
PIXIV_API_ENABLED = False
# ================================================


# ===============检测周期&最低限制=================
# 关注-画师作品检测周期,单位秒,默认1800秒
USERS_CYCLE = 1800
# USERS_CYCLE = 600

# 关注-最低收藏限制,高于LIMIT才会下载,默认3000
USERS_LIMIT = 3000

# 收藏-作品检测周期,单位秒,默认1800秒
BOOKMARK_CYCLE = 1800
# BOOKMARK_CYCLE = 300

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


# ===============数据库连接信息====================
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWD = '123456'
DB_DATABASE = 'moe'
# 建议数据库和表都设置为utf8mb4  
# 插画信息中含有emoji表情
DB_CHARSET = "utf8mb4"
# ================================================