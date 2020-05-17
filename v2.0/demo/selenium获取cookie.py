from selenium import webdriver
import os
import json
import requests
from requests.cookies import RequestsCookieJar

# driver = webdriver.Chrome()
pro_dir = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'

def sele():
	chrome_options = webdriver.ChromeOptions()
	# 静默模式
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--start-maximized')

	chrome_options.add_argument('user-data-dir='+os.path.abspath(pro_dir))
	driver = webdriver.Chrome(chrome_options=chrome_options)

	driver.get('https://www.pixiv.net/')
	cookies = driver.get_cookies()
	        
	with open("pixiv_cookies.txt", "w") as fp:
	    json.dump(cookies, fp)

	driver.close()


def test():
	jar = RequestsCookieJar()
	with open("pixiv_cookies.txt", "r") as fp:
		cookies = json.load(fp)
		for cookie in cookies:
			jar.set(cookie['name'], cookie['value'])
	html = rep(jar)
	print(html.text)

def rep(jar):
	url = 'https://www.pixiv.net/bookmark.php?type=user'
	headers = {
            'referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'origin': 'https://accounts.pixiv.net',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
	html = se.get(url,headers=headers,cookies=jar)
	return html

if __name__ == '__main__':
	sele()
	se = requests.session()
	test()
