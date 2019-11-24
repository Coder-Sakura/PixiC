from selenium import webdriver
from requests.cookies import RequestsCookieJar
import json

from config import COOKIE_NAME,COOKIE_UPDATE_ENABLED,PRO_DIR
HOST_URL = "https://www.pixiv.net/"

class Login(object):

	def __init__(self,cookie_update=COOKIE_UPDATE_ENABLED):	
		self.cookie = self.get_cookie() if cookie_update == True else self.set_cookie()

	# def res(self):
	# 	return self.cookie

	def get_cookie(self):
		'''
		配置selenium以访问站点,保存并返回cookie
		'''
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')	# 静默模式
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--start-maximized')
		chrome_options.add_argument('user-data-dir='+PRO_DIR)	# 用户目录配置
		driver = webdriver.Chrome(chrome_options=chrome_options)
		driver.get(HOST_URL)
		cookies = driver.get_cookies()
		driver.quit()

		with open(COOKIE_NAME, "w") as fp:
		    json.dump(cookies, fp)	# json格式保存

		jar = self.set_cookie()
		return jar

	def set_cookie(self):
		'''
		读取并返回cookie
		'''
		jar = RequestsCookieJar()
		with open(COOKIE_NAME, "r") as fp:
			cookies = json.load(fp)
			for cookie in cookies:
				jar.set(cookie['name'], cookie['value'])
		return jar
		
# Login()
# if __name__ == '__main__':
# 	Login()