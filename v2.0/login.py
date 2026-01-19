# coding=utf8
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from requests.cookies import RequestsCookieJar
import re
import json
import random
import requests

from config import COOKIE_UPDATE_ENABLED,\
	ORIGI_COOKIE_LIST,PRO_DIR,USER_ID
from log_record import logger
from message import TEMP_MSG

# 存储用户cookie的文件名称
COOKIE_NAME = "pixiv_cookie"

headers = {
	"Host": "www.pixiv.net",
	"referer": "https://www.pixiv.net/",
	"origin": "https://accounts.pixiv.net",
	"accept-language": "zh-CN,zh;q=0.9",
	"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
		'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}


class Login(object):

	def __init__(self):
		"""
		初始化操作
		flag用于判断是否需要请求以获得uid
		cookie用于存储selenium获取的cookie
		"""
		self.host_url = "https://www.pixiv.net/"
		self.flag = True if USER_ID == "" else False
		self.user_id = USER_ID if USER_ID != "" else ""
		self.isExists_UserCookie = True if ORIGI_COOKIE_LIST != [] else False
		# uid为空,而cookie又随机
		self.cookie_list = []
		# self.RCJar = RequestsCookieJar()
		# self.cookie = RequestsCookieJar()
		self.class_name = self.__class__.__name__

	def add_cookie(self,pending_cookie):
		"""
		判断向self.cookie_list添加cookie
		"""
		if pending_cookie not in self.cookie_list and \
		   type(pending_cookie) == type(RequestsCookieJar()):
			self.cookie_list.append(pending_cookie)

	def reload_cookie_list(self,pending_cookie):
		"""
		TBD:重载cookie
		pending_cookie为None
			复制一份cookie_list
			调用check函数
			-->成功
				使用新cookie_list清空复制出来的
		pending_cookie不为None则清空cookie_list,并append pending_cookie
		return True/
		"""
		pass
		
	def check(self):
		"""
		用于在启动多进程前,获取并校验cookie和uid的获取
		"""
		logger.info(TEMP_MSG["GET_COOKIE_INFO"].format(self.class_name))
		# 检查是否能支持用户自定义cookie
		if self.isExists_UserCookie:
			try:
				self.str2CookieJar()
			except Exception as e:
				logger.warning(f"<Exception> - {e}")
				logger.warning(TEMP_MSG["CONVERT_COOKIEJAR_ERROR_INFO"].format(self.class_name))
				exit()
		# 检查是否能通过selenium/本地cookie文件获取
		else:
			self.get_cookie() if COOKIE_UPDATE_ENABLED == True else self.set_cookie()
			if self.cookie_list == []:
				logger.warning(TEMP_MSG["LOGIN_ERROR_INFO"].format(self.class_name))
				exit()

		# 检查是否能获取user_id
		if self.flag:
			self.user_id = self.get_user_id()

		logger.info(TEMP_MSG["INIT_INFO"].format(self.class_name))

	def get_cookie(self):
		'''
		配置selenium以访问站点,持久化cookie 
		'''
		logger.warning(TEMP_MSG["GET_COOKIE_NOW_INFO"].format(self.class_name))
		chrome_options = webdriver.ChromeOptions()
		# 静默模式可能会导致获取不了cookie
		# chrome_options.add_argument('--headless')	
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--start-maximized')
		# 取消警告语
		chrome_options.add_experimental_option('useAutomationExtension', False)
		chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
		# 用户目录配置
		chrome_options.add_argument('user-data-dir='+PRO_DIR)

		try:
			# 兼容新版 Selenium：使用 options 参数
			driver = webdriver.Chrome(options=chrome_options)
			# selenium.common.exceptions.WebDriverException: 
			# Message: unknown error: cannot create default profile directory
			# PRO_DIR错误
		except InvalidArgumentException as e:
			logger.warning(TEMP_MSG["GET_COOKIE_NOW_INFO"].format(self.class_name))
			exit()
		else:
			driver.get(self.host_url)
			cookies = driver.get_cookies()
			driver.quit()

			with open(COOKIE_NAME, "w") as fp:
				json.dump(cookies, fp)
			self.set_cookie()
			
	def set_cookie(self):
		'''
		读取并添加cookie
		'''
		try:
			with open(COOKIE_NAME, "r", encoding="utf8") as fp:
				# readlines(),读取之后,文件指针会在文件末尾,再执行只会读到空[]
				if fp.readlines() == []:
					logger.warning(TEMP_MSG["COOKIE_EMPTY_INFO"].format(self.class_name))
					exit()
				fp.seek(0)
				cookies = json.load(fp)
				RCJar = RequestsCookieJar()
				for cookie in cookies:
					RCJar.set(cookie['name'], cookie['value'])
					# self.cookie.set(cookie['name'], cookie['value'])
				self.add_cookie(RCJar)
		except FileNotFoundError as e:
			logger.warning(TEMP_MSG["FILE_NOT_FOUND_INFO_1"].format(self.class_name))
			logger.warning(TEMP_MSG["FILE_NOT_FOUND_INFO_2"].format(self.class_name))
			logger.warning(f"<FileNotFoundError> - {e}")
			exit()
		
		# 获取user_id
		# if self.flag:
		# 	self.user_id = self.get_user_id()
		# else:
		# 	self.user_id = USER_ID
		# return self.cookie

	def get_user_id(self):
		resp = requests.get(self.host_url,headers=headers,cookies=random.choice(self.cookie_list)).text
		if "Please turn JavaScript on and reload the page." in resp:
			logger.warning(TEMP_MSG["GOOGLE_CAPTCHA_ERROR_INFO"].format(self.class_name))
			exit()
		user_id = re.findall(r'''.*?,user_id:"(.*?)",.*?''',resp.replace(" ",""))[0]
		return user_id

	def subprocess_check(self):
		"""
		子进程调用,不存在2个都为空,主进程一开始会check检查是否通过
		"""
		if self.isExists_UserCookie:
			self.str2CookieJar()
		else:
			self.set_cookie()

		if self.flag:
			self.user_id = self.get_user_id()

		return self.cookie_list

	def str2CookieJar(self):
		for oc in ORIGI_COOKIE_LIST:
			cookie_dict = {}
			for i in oc.split(";"):
				n,v = i.strip().split("=",1)
				cookie_dict[n] = v
			cookie = requests.utils.cookiejar_from_dict(cookie_dict)
			self.add_cookie(cookie)

client = Login()