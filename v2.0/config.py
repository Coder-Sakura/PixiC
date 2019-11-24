# import hashlib
# h = hashlib.md5()
# h.update(bytes(__file__,encoding='utf-8'))
# COOKIE_NAME = h.hexdigest()
# print(COOKIE_NAME)
# 加密txt

# 路径
ROOT_PATH = r'H:\se19'
# ROOT_PATH = None

PRO_DIR = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'

# url
# HOST_URL = "https://www.pixiv.net/"

# 存储Cookie的文件名
COOKIE_NAME = 'pixiv_cookie'

# 已成功获取过cookie,可设为False
# 登录失败请设置为True,重新获取cookie
# 首次运行请设置为True,默认为True
COOKIE_UPDATE_ENABLED = True

# 数据库连接信息
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWD = '123456'
DB_DATABASE = 'test'
# DB = 'moe' pixiv表
DB_CHARSET = "utf8"
