# coding=utf8

# ================== FOLDER ==================
ROOT_PATH = r''							# 关注画师作品存放路径, 路径为空时在脚本目录创建
BOOKMARK_PATH = r''						# 收藏作品存放路径, 路径为空时在脚本目录创建

# Chrome浏览器用户数据目录, 通常只需将 Users 更改为你的用户名
# PRO_DIR = r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data'
PRO_DIR = r''
# ================== FOLDER ==================


# ================== LOGIN ==================
USER_ID = ''							# Pixiv 账户的 uid

"""
1. 启用以持久化 Chrome 已登录的 Pixiv 账号信息
2. 建议: 首次运行启用, 后续运行设置为 False
3. 若不想配置 Chrome, 配置此项为 False 并配置 ORIGI_COOKIE_LIST
"""
COOKIE_UPDATE_ENABLED = True
# COOKIE_UPDATE_ENABLED = False

"""
1. 配置 cookie, 一行一个完整cookie
2. 多个 cookie 时请配置 USER_ID, 否则从中随机一个进行获取
"""
ORIGI_COOKIE_LIST = []
# ================== LOGIN ==================


# ================== LOOP & LIMIT ==================
SKIP_EXISTS_ILLUST = True							# 增量&快速更新 默认开启
													# 启用时不更新数据库数据,减少请求次数
SLOW_MODE = True									# 慢速模式抓取 线程数固定为1 默认开启 不建议改动
													# 配置为 False 以开启快速模式

PIXIV_CRAWLER_ENABLED = False						# 关注画师模块开关 默认关闭
PIXIV_BOOKMARK_ENABLED = True						# 收藏作品模块开关 默认开启
BOOKMARK_HIDE_ENABLE = False						# 除非有未公开收藏否则关闭
THREAD_NUM = 4										# 为关注画师/收藏作品模块各分配的线程数 不建议改动
LOOP_LIMIT = 0										# 单轮次各模块抓取上限 默认0 0为不限制
													# 建议增量&快速更新设置为8000,避免过多请求导致账号被封

USERS_CYCLE = 86400									# 关注画师 检测周期 默认86400秒
USERS_LIMIT = 3000									# 关注画师作品 最低下载收藏数 默认3000
													# 仅收集作品元数据 可设置为99999

BOOKMARK_CYCLE = 86400								# 收藏作品 检测周期 默认86400秒
BOOKMARK_LIMIT = 0									# 收藏作品作品 最低下载收藏数 默认0
													# 仅收集作品元数据 可设置为99999
# ================== LOOP & LIMIT ==================


# ================== API ==================
PIXIV_API_ENABLED = False					# API 控制开关 默认关闭
API_HOST = '0.0.0.0'
API_PORT = '1526'
API_THREAD = 8								# API 数据库线程数
RANDOM_LIMIT = 10							# random 接口最大返回数
# ================== API ==================


# ================== DataBase ==================
DB_ENABLE = False								# 数据库开关 默认关 不启用时API不生效
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWD = 'root'
DB_DATABASE = 'moe'
DB_CHARSET = 'utf8mb4'
# ================== DataBase ==================

# ===============DEBUG===============
DEBUG = False
# ===============DEBUG===============