# coding=utf8
# ================================================
# 关注画师路径为空时,在脚本当前路径创建pixiv_crawler文件夹
# 示例,D:\author
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
# USER_ID,即uid.用于获取对应用户的关注, 收藏作品.
# 1.一般是填写自己的账号下载关注画师作品和收藏插画
# 2.填写他人的uid时并选择其他目录作为下载目录, 避免下载混乱
USER_ID = ""


"""
1. 设置此项以配置 启动Chrome将登录的Pixiv账号信息保存到本地
文件名: pixiv_cookie
2. 首次运行请设置为True,后续运行建议设置为False
3. 若不想配置Chrome,可将此项设置为False,
然后进行自定义cookie的配置(ORIGI_COOKIE_LIST)
"""
COOKIE_UPDATE_ENABLED = True
# COOKIE_UPDATE_ENABLED = False


"""
1. 自定义cookie,将下列的user_cookie替换为你的pixiv cookie
2. 若有多个,则依次复制替换,注意结尾的','
ORIGI_COOKIE_LIST = [
	'user_cookie1',     
	'user_cookie2',
]

[WARNING]
1. 注意! 当自定义多个cookie时, 请填写'USER_ID'字段
2. 否则将从多个cookie中随机选取一个以获得对应的USER_ID
"""
ORIGI_COOKIE_LIST = []
# ================================================


# =============== 控制开关 ===============
# 一般用于增量/快速更新,默认为开
# 1.打开此开关将不再请求已下载到ROOT_PATH/BOOKMARK_PATH的pid插画
# 2.同时也无法更新对应pid在数据库中的记录
SKIP_ISEXISTS_ILLUST = True

# 关注画师爬虫控制开关
PIXIV_CRAWLER_ENABLED = False

# 收藏作品爬虫控制开关
PIXIV_BOOKMARK_ENABLED = True
# 是否获取未公开收藏, 默认关闭
# - USER_ID与pixiv_cookie为本人账号时,建议开启此项)
# - USER_ID与pixiv_cookie非本人账号时,建议关闭此项)
BOOKMARK_HIDE_ENABLE = False

# API控制开关
PIXIV_API_ENABLED = False
# ========================================


# =============== 检测周期 & 最低下载限制 ===============
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
# ======================================================


# ================== API设置 =======================
API_HOST = '0.0.0.0'
# 2020/5/10 pixiv网站排名 + 5
API_PORT = '1526'
# API数据库线程数
API_THREAD = 8
# API-random接口-最大返回数
RANDOM_LIMIT = 10
# =================================================


# =============== 数据库连接信息 ===================
# 数据库开关, 默认为关
# True - 数据入库
# False - 不使用数据库, 同时API也无法使用
# DB_ENABLE = True
DB_ENABLE = False

# create.sql在doc目录下
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'pixiv'
DB_PASSWD = 'Huawei12#$'
DB_DATABASE = 'moe'
DB_CHARSET = "utf8mb4"
# ================================================

# ===============DEBUG===============
# TODO
DEBUG = False
# ===============DEBUG===============


# =============== 爬取节奏控制 ===============
# 开启后将放慢“页面/信息”请求速率，降低触发网站风控概率；
# 图片/文件下载速度不受该开关影响。
SLOW_CRAWL_ENABLED = True
# 慢速爬取的随机等待区间（秒）
SLOW_CRAWL_MIN_DELAY = 1
SLOW_CRAWL_MAX_DELAY = 3
# ============================================