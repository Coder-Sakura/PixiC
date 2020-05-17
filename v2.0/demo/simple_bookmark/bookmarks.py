# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning     #强制取消警告
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar
from selenium import webdriver
from PIL import Image   #转换格式
import zipfile  #解压缩
import os
import time
import re
import json
import imageio          #合成gif
import math     #用ceil
from http.cookiejar import CookieJar

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)      #强制取消警告
se = requests.session()

se.cookies = CookieJar()

se.mount('http://', HTTPAdapter(max_retries=1))
se.mount('https://', HTTPAdapter(max_retries=1))

class Pixiv():  
	# 收藏的作品
    def __init__(self):
        self.headers = {
            'referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'origin': 'https://accounts.pixiv.net',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        self.bookmark = 'https://www.pixiv.net/bookmark.php?rest=show&p='                                    #收藏url
        self.path = u'H:\\bookmark'
        self.jar = RequestsCookieJar()

    def new_login(self):
        pro_dir = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-data-dir='+os.path.abspath(pro_dir))
        
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('https://www.pixiv.net/')
        cookies = driver.get_cookies()
        
        with open("pixiv_cookie", "a") as fp:  # 不直接利用,存下来保存比较好
            json.dump(cookies, fp)

        driver.quit()
        jar = self.get_cookies()
        if jar == []:
            print("请使用Chrome浏览器进行登录,以便获取cookie")
            print("请打开代理软件")
            exit()
        return jar

    def get_cookies(self):
        jar = RequestsCookieJar()
        with open("pixiv_cookie", "a") as fp:
            cookies = json.load(fp)
            for cookie in cookies:
                jar.set(cookie['name'], cookie['value'])
        return jar

    def attention_html(self):       
    	# 获取关注画师界面的各种信息
        attention_html = self.request(self.bookmark)
        attention_html_soup = BeautifulSoup(attention_html.text, 'lxml')
        max_num = attention_html_soup.find('span', attrs={'class', 'count-badge'}).text[:-1]     #获取最大收藏件数
        integer_max_num = math.ceil(int(max_num)/20)
        print('收藏作品数为%s' % (max_num))
        print('收藏共有%s页' % (integer_max_num))

        A,B,C = 0,0,0
        for num in range(1,int(integer_max_num)+1):
            attention_html_url = self.bookmark + str(num)   #每个收藏url
            attention_html = self.request(attention_html_url)
            attention_html_soup = BeautifulSoup(attention_html.text,'lxml')
            painter_information = attention_html_soup.find('ul',attrs={'class','_image-items'}).find_all('li',attrs={'class','image-item'})  #作品
            li_gather = list(painter_information)   #li 标签集合
            a,b,c = 0,0,0
            for i_num,i in enumerate(li_gather):
                try:
                    folder_id = list(list(list(i)[1])[0])[0]['data-id']   #a标签往下一层2个div,我们需要的信息在第一个div下的img的data-id、data-src属性  作品id        页数在第二个div
                except:
                    print("作品被作者删除了!")
                    break
                small_url = list(list(list(i)[1])[0])[0]['data-src']
                if "https://s.pximg.net/common/images" in small_url:

                    print("作品被作者删除了!")
                    break
                self.mkdir_works(folder_id)     # 已经切换到self.path\\folder_id目录下
                print('\n')
                print('第%s页收藏的第%s个作品：' % (str(num),i_num+1))
                folder_path = self.path + '\\' + folder_id
                if 'ugoku-illust' in list(i)[1]['class']:   # li标签的第一个对象的class,也就是用来判断图片类型的那个a标签的class
                    a += 1          # print('动图')
                    print('正在下载动图...')
                    self.img_gif(folder_id,folder_path)
                else:
                    if 'multiple' in list(i)[1]['class']:
                        page = list(list(list(i)[1])[1])[1].text
                        b += 1      # print('多图')
                        print('正在下载多图(%s)...' % (page))
                        self.img_multi(folder_id,small_url,page,folder_path)
                    else:
                        c += 1      # print('单图')
                        print('正在下载单图...')
                        self.img_single(folder_id,small_url,folder_path)
            print('\n第%s页下载完成' % (str(num)))
            print('分别:动图{},多图{},单图{}\n'.format(a,b,c))
            A = A + a
            B = B + b
            C = C + c         
        print('\n总的 动图{}多图{}单图{}'.format(A,B,C))
        print('下载完成！！！！\n')      

    def mkdir_works(self,folder_id):
        os.chdir(self.path)
        isExists = os.path.exists(os.path.join(self.path,folder_id))
        if not isExists:
            print(u'[在',self.path,'下建了一个', folder_id, u'文件夹！]')
            os.makedirs(os.path.join(self.path,folder_id))
            os.chdir(os.path.join(self.path,folder_id)) ##切换到目录
            return True
        else:
            os.chdir(os.path.join(self.path,folder_id)) ##切换到目录
            print(u'[在',self.path,'下已经有', folder_id, u'文件夹！]')
            return False

    def img_single(self,folder_id,small_url,folder_path):
        print('当前目录',folder_path)
        work_name = folder_id + '.jpg'
        jpg_judge_path = folder_path + '\\' + work_name
        png_judge_path = folder_path + '\\' + folder_id + '.png'
        if os.path.exists(jpg_judge_path) == True and os.path.getsize(jpg_judge_path) > 1000:
            print(jpg_judge_path,'已存在且字节数不为58！')
        else:
            if os.path.exists(png_judge_path) == True and os.path.getsize(png_judge_path) > 1000:
                print(png_judge_path,'已存在且字节数不为58！')
            else:
                try:
                    r = r'''.*?([0-9]{4}/[0-9]{2}/.*?_p).*?'''
                    p = re.compile(r)
                    small_date = re.findall(p,small_url)[0]

                    head = 'https://i.pximg.net/img-original/img/'
                    img_url = head + small_date + str(0) + small_url[-4:]        #.jpg
                    img_html = self.request(img_url)
                    size = self.down(img_html,work_name,jpg_judge_path)
                    if size == 58:
                        time.sleep(3)
                        print('{}格式不对，准备重下'.format(work_name))
                        img_url = head + small_date + str(0) + '.png'
                        img_html = self.request(img_url)
                        self.down_conversion(img_html,folder_id,jpg_judge_path,png_judge_path)
                except Exception as e:
                    print(img_url)
                    print(work_name,'下载失败')

    def img_multi(self,folder_id,small_url,page,folder_path):
        print('当前目录',folder_path)
        for img_num in range(0,int(page)):
            work_name = folder_id + '-' + str(img_num) + small_url[-4:]       
            jpg_judge_path = folder_path + '\\' + work_name
            png_judge_path = folder_path + '\\' + folder_id + '-' + str(img_num) + '.png'
            
            if os.path.exists(jpg_judge_path) == True and os.path.getsize(jpg_judge_path) > 1000:
                print(jpg_judge_path,'已存在且字节数不为58！')
            else:
                if os.path.exists(png_judge_path) == True and os.path.getsize(png_judge_path) != 58:   #判断png
                    print(png_judge_path,'已存在且字节数不为58！')
                else:
                    try:
                        r = r'''.*?([0-9]{4}/[0-9]{2}/.*?_p).*?'''
                        p = re.compile(r)
                        small_date = re.findall(p,small_url)[0]

                        head = 'https://i.pximg.net/img-original/img/'
                        img_url = head + small_date + str(img_num) + small_url[-4:]        #.jpg

                        img_html = self.request(img_url)
                        size = self.down(img_html,work_name,jpg_judge_path)

                        if size == 58:
                            print('{}格式不对，准备重下'.format(work_name))
                            img_url = head + small_date + str(img_num) + '.png'
                            img_html = self.request(img_url)
                            self.down_conversion(img_html,folder_id,jpg_judge_path,png_judge_path,img_num)
                    except:
                        print(img_url)
                        print(work_name,'下载失败')

    def img_gif(self,folder_id,folder_path):     
        gif_judge_path = folder_path + '\\' + folder_id + '.gif'
        if os.path.exists(gif_judge_path) == True and os.path.getsize(gif_judge_path) != 58:
            print(gif_judge_path,'已存在且字节数不为58！')
        else:
            zip_url = 'https://www.pixiv.net/ajax/illust/' +folder_id + '/ugoira_meta'      #压缩包网址
            zip_html = self.request(zip_url)
            zip_json = json.loads(zip_html.text)          #
            zip_originalSrc = zip_json["body"]["src"]
            delay = 1/(zip_json["body"]["frames"][0]['delay']/1000)     #80(ms)/1000 -> 0.08(s)
            print('帧率:',delay)       
            self.headers['Referer'] = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + folder_id
            gif_html = self.request(zip_originalSrc)
            zip_name = folder_id + '.zip'
            f = open(zip_name, 'ab')        #下载zip
            f.write(gif_html.content)       
            f.close()
            f = zipfile.ZipFile(zip_name,'r')   #解压zip
            for file in f.namelist():
                f.extract(file,".")
            f.close()
            print('解压完成')
            os.remove(zip_name)             # 删除压缩包
            gif_name = folder_id + '.gif'   # gif图片name
            frames = []                     # 用来存储要进行合成gif的图片
            files = os.listdir(folder_path) # 扫描当前作品目录下的文件
            print('开始合成')
            for image_num in range(1,len(files)):
                frames.append(imageio.imread(files[image_num]))
            imageio.mimsave(gif_name, frames, 'GIF', fps  = delay) # 间隔
            print('%s 完成\t大小为%.2f'%(gif_name,os.path.getsize(gif_judge_path)/float(1024*1024)))
            for file in files:
                os.remove(file)

    def down(self,img_html,work_name,jpg_judge_path):
        f = open(work_name, 'ab')
        f.write(img_html.content)   
        f.close()
        print('%s完成\t大小为%.2f'%(work_name,os.path.getsize(jpg_judge_path)/float(1024*1024)))
        return os.path.getsize(jpg_judge_path)

    def down_conversion(self,img_html,folder_id,jpg_judge_path,png_judge_path,img_num=None):
        if os.path.exists(jpg_judge_path) == True:
            os.remove(jpg_judge_path)
            print('格式错误的文件已删除')
        if img_num == None:
            work_name = folder_id + '.png'
        else:
            work_name = folder_id + '-' + str(img_num) + '.png'
        f = open(work_name, 'wb')
        f.write(img_html.content)
        f.close()
        print('%s完成\t大小为%.2f'%(work_name,os.path.getsize(png_judge_path)/float(1024*1024)))

    def request(self,url,num_entries = 5):
        try:
            content = se.get(url, headers=self.headers, cookies=self.jar, verify=False, timeout=10)
            return content
        except:
            print('error...')
            if num_entries > 0:
                print('剩余重试次数:%s' % (num_entries))
                return self.request(url,num_entries = num_entries - 1)
            else:
                print('代理无效或网络错误')

    def work(self):
        print('开始模拟登陆...')
        self.jar = self.new_login()
        self.attention_html()
pixiv = Pixiv()
pixiv.work()

