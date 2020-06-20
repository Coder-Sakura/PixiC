# coding=utf8
from selenium import webdriver
from requests.cookies import RequestsCookieJar
import json
import re
import requests

from config import *
from logstr import log_str
from message import *

# 存储用户cookie的文件名称
COOKIE_NAME = "pixiv_cookie"

class Login(object):

	def __init__(self):
		"""
		初始化操作
		flag用于判断是否需要请求以获得uid
		cookie用于存储selenium获取的cookie
		"""
		self.host_url = "https://www.pixiv.net/"
		self.user_id = ""
		self.flag = True if USER_ID == "" else False
		self.cookie = RequestsCookieJar()
		self.class_name = self.__class__.__name__
		
	def check(self):
		"""
		获取cookie
		"""
		log_str(GET_COOKIE_INFO.format(self.class_name))
		# 条件表达式,将cookie对象赋值给self.cookie
		self.get_cookie() if COOKIE_UPDATE_ENABLED == True else self.set_cookie()
		if self.cookie == []:
			log_str(LOGIN_ERROR_INFO.format(self.class_name))
			exit()
		log_str(INIT_INFO.format(self.class_name))

	def get_cookie(self):
		'''
		配置selenium以访问站点,持久化cookie
		'''
		log_str(GET_COOKIE_NOW_INFO.format(self.class_name))
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
		driver = webdriver.Chrome(chrome_options=chrome_options)
		driver.get(self.host_url)
		cookies = driver.get_cookies()
		driver.quit()

		with open(COOKIE_NAME, "w") as fp:
		    json.dump(cookies, fp)
		    print(cookies)
		    for _ in cookies:
		    	self.cookie.set(_['name'], _['value'])

	def set_cookie(self):
		'''
		读取并返回cookie
		'''
		try:
			with open(COOKIE_NAME, "r", encoding="utf8") as fp:
				# readlines(),读取之后,文件指针会在文件末尾,再执行只会读到空[]
				if fp.readlines() == []:
					log_str(COOKIE_EMPTY_INFO.format(self.class_name))
					exit()
				fp.seek(0)
				cookies = json.load(fp)
				for cookie in cookies:
					self.cookie.set(cookie['name'], cookie['value'])
		except FileNotFoundError as e:
			log_str(FILE_NOT_FOUND_INFO_1.format(self.class_name))
			log_str(FILE_NOT_FOUND_INFO_2.format(self.class_name))
			log_str(e)
			exit()
		
		# 获取user_id
		if self.flag == True:
			self.user_id = self.get_user_id()
		else:
			self.user_id = USER_ID
		return self.cookie

	def get_user_id(self):
		user_id = re.findall(r'''.*?,user_id:"(.*?)",.*?''',requests.get(self.host_url,cookies=self.cookie).text.replace(" ",""))[0]
		return user_id

client = Login()