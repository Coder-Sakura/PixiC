# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from lxml import etree

import os
import time
import re
import random
import json

# 动图
from PIL import Image   #转换格式
import imageio  #合成gif
import zipfile  #解压缩
#强制取消警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning     
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar
from selenium import webdriver

from http.cookiejar import CookieJar
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)      #强制取消警告
se = requests.session()
se.cookies = CookieJar()
# se.trust_env = False   # 全局代理问题
se.mount('http://', HTTPAdapter(max_retries=1))
se.mount('https://', HTTPAdapter(max_retries=1))

class Pixiv():

    def __init__(self):
        self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'   #获取postkey
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'                                                 #登录# self.target_url = 'http://www.pixiv.net/search.php?' \# 'word=1&order=date_d&p='
        # self.target_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='                              #从画师作品界面点击图片跳转的url
        # self.main_url = 'http://www.pixiv.net/member_illust.php?id='                                                    #画师用户个人url
        self.user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
                    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"]
        # 'referer': 'https://accounts.pixiv.net/login',
        self.headers = {
            'referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'origin': 'https://accounts.pixiv.net',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            # 'cookie':'first_visit_datetime_pc=2019-06-30+14%3A02%3A10; p_ab_id=7; p_ab_id_2=2; p_ab_d_id=1741459444; _ga=GA1.2.1541262787.1560534037; privacy_policy_agreement=1; c_type=20; a_type=0; b_type=0; module_orders_mypage=%5B%7B%22name%22%3A%22sketch_live%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22tag_follow%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22recommended_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22everyone_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22following_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22mypixiv_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22spotlight%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22fanbox%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22featured_tags%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22contests%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22user_events%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22sensei_courses%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22booth_follow_items%22%2C%22visible%22%3Atrue%7D%5D; yuid_b=KSKZB1M; login_ever=yes; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^6=user_id=27858363=1^9=p_ab_id=7=1^10=p_ab_id_2=2=1^11=lang=zh=1; ki_r=; __utmz=235335808.1561936687.5.3.utmcsr=pixiv.help|utmccn=(referral)|utmcmd=referral|utmcct=/hc/zh-tw; limited_ads=%7B%22responsive%22%3A%22%22%7D; categorized_tags=3ze0RLmk59~6sZKldb07K~HLWLeyYOUF~OT-C6ubi9i~jfnUZgnpFl; tag_view_ranking=jfnUZgnpFl~SQZaakhtVv~uW5495Nhg-~DHqIUplIEc~b3tIEUsHql~Lt-oEicbBr~RTJMXD26Ak~GF09UjQt_e~gVfGX_rH_Y~jH0uD88V6F~kwQ7-a01CG~-fP8ij-3EX~3W4zqr4Xlx~kGYw4gQ11Z~MSNRmMUDgC~8ch4HlASni~Cj_Gcw9KR1~kW8varCrdB~1yIPTg75Rl~NIpEilHR4P~5oPIfUbtd6~OYl5wlor4w~NNraL54MQl~eYIfp1VgVQ~U9A9K0M8Oi; p_b_type=1; device_token=205af45342716361b4dff3fde8e51c15; is_sensei_service_user=1; _gid=GA1.2.1295270473.1565421992; __utmc=235335808; tags_sended=1; login_bc=1; ki_t=1561871297792%3B1565423294286%3B1565423294286%3B4%3B16; __utma=235335808.988886957.1561870925.1565421994.1565426875.15; __utmt=1; __utmb=235335808.1.10.1565426875; _gat=1; PHPSESSID=27858363_050406b681a63254195a7d8484a6a4d8'
            }
        self.jar = RequestsCookieJar()
        self.pixiv_id = '1508015265@qq.com'
        self.password = '2016zhangjzJZ'
        # 密码采用getpass.getpass('')隐藏输入
        self.post_key = ''
        self.return_to = 'https://www.pixiv.net/bookmark.php?type=user&rest=show&p='                                    #关注画师总页面                                                                   #拼接画师个人主页url    
        self.path = 'H:\se18'
        # self.xici_headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
        #     "Host": "www.xicidaili.com"
        # }
        self.agent_ip_list = []
        self.error_ip_list = []
        self.father_folder = ''

    # 无法使用
    def login(self):       
        '''
        1.P站登录改变
        2.防止多次登录,保存cookie,目前2种方法：手动和selenium,还未破解
        login方法重写为无cookie时模拟登录获取cookie并保存到本地,有则直接读取
        '''
        post_key_html = se.get(self.base_url,headers=self.headers)
        post_key_soup = BeautifulSoup(post_key_html.text, 'lxml')
        self.post_key = post_key_soup.find('input')['value']
        print(self.post_key)    #捕获postkey
        # v3_token = self.v3()
        data = {
            'captcha':'',
            'g_recaptcha_response':'',
            'password': self.password,
            'pixiv_id': self.pixiv_id,
            'post_key': self.post_key,
            'source':'pc',
            'ref':'',
            'return_to': 'https://www.pixiv.net/',
            # 'source':'pc',
            # 'recaptcha-v3-token':v3_token
            }
        headers = self.headers
        # headers['cookie'] = '_ga=GA1.3.1541262787.1560534037; _gid=GA1.3.1107149500.1561844268; p_ab_id=7; p_ab_id_2=2; p_ab_d_id=1741459444; _ga=GA1.2.1541262787.1560534037; _gid=GA1.2.1107149500.1561844268; login_bc=1; device_token=59e9673172a9ed639ae020391ea35225; privacy_policy_agreement=1; c_type=20; a_type=0; b_type=0; module_orders_mypage=%5B%7B%22name%22%3A%22sketch_live%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22tag_follow%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22recommended_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22everyone_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22following_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22mypixiv_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22spotlight%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22fanbox%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22featured_tags%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22contests%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22user_events%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22sensei_courses%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22booth_follow_items%22%2C%22visible%22%3Atrue%7D%5D; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^6=user_id=27858363=1^9=p_ab_id=7=1^10=p_ab_id_2=2=1^11=lang=zh=1; tag_view_ranking=kwQ7-a01CG~-fP8ij-3EX~3W4zqr4Xlx~kGYw4gQ11Z~MSNRmMUDgC~8ch4HlASni~Cj_Gcw9KR1~kW8varCrdB~1yIPTg75Rl~NIpEilHR4P~Lt-oEicbBr~5oPIfUbtd6~OYl5wlor4w~NNraL54MQl~eYIfp1VgVQ~U9A9K0M8Oi; __utmc=235335808; PHPSESSID=27858363_d9f2f0121462b64edf213279f63b7551; p_b_type=1; __utma=235335808.988886957.1561870925.1561905185.1561907582.3; __utmz=235335808.1561907582.3.2.utmcsr=accounts.pixiv.net|utmccn=(referral)|utmcmd=referral|utmcct=/login; __utmt=1; __utmb=235335808.1.10.1561907582'
        rep = se.post(self.login_url, data=data, headers=headers)
        if "success" in rep.text:
            print('登录成功...')
        else:
            print(rep.text)
            exit()
        # if '桜花树下宇焉酱' in rep.text:
        #     print('登陆成功')# print(rep.text)        # self.test()

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
        
        with open("pixiv_cookies.txt", "w") as fp:  # 不直接利用,存下来保存比较好
            json.dump(cookies, fp)

        driver.quit()
        jar = self.get_cookies()
        return jar

    def get_cookies(self):
        jar = RequestsCookieJar()
        with open("pixiv_cookies.txt", "r") as fp:
            cookies = json.load(fp)
            for cookie in cookies:
                jar.set(cookie['name'], cookie['value'])
        return jar
    
    def attention_html(self):       #获取关注画师界面的各种信息
        attention_html = self.request(self.return_to)
        # 获取最大关注画师页数
        attention_html_soup = BeautifulSoup(attention_html.text, 'lxml')
        # print(attention_html_soup)
        max_num = attention_html_soup.find('div', attrs={'class', '_pager-complex'}).find_all('li')[-2].text     #获取最大页数

        # 获取当前pixiv_token,并自动收藏
        # soup = BeautifulSoup(attention_html.text, "html.parser")
        # pattern = re.compile(r'pixiv.context.token = "(.*?)";$', re.MULTILINE | re.DOTALL)
        # script = soup.find("script", text=pattern)
        # print('pixiv.context.token:',pattern.search(script.text).group(1))

        # tt = pattern.search(script.text).group(1)
        # data = {
        #     'mode': 'save_illust_bookmark',
        #     'illust_id':'75524460',
        #     'restrict':'0',
        #     'comment':'',
        #     'tags':'',
        #     'tt':tt
        # }
        # rep = se.post('https://www.pixiv.net/rpc/index.php',data=data,headers=self.headers)
        # print(rep.text)
        # exit()
        '''
        取消收藏,需要tt以及book_id[]，也就是收藏成功后会给你一个随机的bookmark_id，取消收藏时需要提交这个id
        bookmark_id获取方法:可以保存收藏post请求的resp里的;或者是从收藏页面获取。
        如果是批量取消收藏，那么可以先获取第一页所有作品的bookmark_id，然后一个个取消收藏
        '''
        
        print('最大页数为%s\n' % (max_num))
        for num in range(1,int(max_num)+1):     #第一页下载完了
        # for num in range(2,int(max_num)+1):
            attention_html_url = self.return_to + str(num)      #关注界面的4个url   https://www.pixiv.net/bookmark.php?type=user&rest=show&p= + str(num)
            attention_html = self.request(attention_html_url)
            attention_html_soup = BeautifulSoup(attention_html.text,'lxml')
            painter_information = attention_html_soup.find('div', attrs={'class', 'members'}).find_all('div', attrs={'class', 'userdata'})  #画师个人信息
            for painter in painter_information:                 # name = painter.a.get_text()                                                       # exp: '灼热之痕'
                painter_id = painter.a['data-user_id']                                              # xxxxxxx
                name = painter.a['data-user_name']#知道画师id和name,可以先创建id+name的文件夹                
                self.father_folder = self.mkdir_painter(painter_id,name)
                ajax_url = 'https://www.pixiv.net/ajax/user/' + painter_id + '/profile/all'         # 画师作品id总数据url  # href = self.host_pixiv + painter.a['href']                            # https://www.pixiv.net/ + member.php?id=xxxxxxx,应该是https://www.pixiv.net/ajax/user/xxxxxxx/profile/all          
                self.painter_picture(painter_id,ajax_url,name)
            # 每个画师作品获取完休眠5s
            # time.sleep(10)
        # 每页的画师作品获取完之后休眠10s
        # time.sleep(10)
        print('下载完成！！！！')   

    def painter_picture(self,painter_id,ajax_url,name):    #画师个人
        ajax_html = self.request(ajax_url)
        ajax_json = json.loads(ajax_html.text)          #作品id数据 大集合          #动图也在illusts，可以考虑下载失败报id，让手动下载
        ajax_illusts = ajax_json["body"]["illusts"]     #单图和多图 dict类型        #ajax_illusts 和 ajax_manga 相加，然后通过冒泡排序排序好，从大到小，因为越大的id代表时间越接近现实时间
        ajax_manga = ajax_json["body"]["manga"]         #漫画和多图一样         #返回的是一个大到小的列表，然后从中每 48 个进行拼接得到works_url,也就是作品数据url                                               
        # print(name,painter_id)
        # print('ajax_illusts有',len(ajax_illusts))    #插画
        # print('ajax_manga有',len(ajax_manga))        #漫画，漫画与多图获取原图方式一样
        if len(ajax_manga) == 0:                        #假如画师没有manga类的作品，所以需要判断 len(ajax_manga)
            total_data_dict = dict(ajax_illusts)
        else:
            total_data_dict = dict(ajax_illusts, **ajax_manga)  #字典合并     
        total_data = list(total_data_dict.keys())           #取字典的keys，并转化为list
        len_total = len(total_data)
        for x in range(len_total-1):        #冒泡排序，输出小大
            for y in range(len_total-1-x):
                if total_data[y] > total_data[y+1]:
                    total_data[y],total_data[y+1] = total_data[y+1],total_data[y]
        total_data = total_data[::-1]       # 通过分片，列表反转,输出大小        # list去重操作，list(set(list_name));list排序，list.sort(list_name)                
        limit_num = 48  #按每48个分组
        after_grouping_list = [total_data[i:i+limit_num] for i in range(0,len(total_data),limit_num)]     #分组好的列表的集合 list ，每个列表48个作品id
        print('画师',name,'作品有：',len(after_grouping_list),'页')             # after_grouping_list被分为多少组, 1247/48取整26 ceil(len(total_data)/limit_num) #向上取整
        count = 0           #计算多少次拼接url
        single_graph = 0    #单图
        multi_graph = 0     #多图
        gif_graph = 0
        for grouping_list in after_grouping_list:   # grouping_list list类型
            # 1.https://www.pixiv.net/ajax/tags/frequent/illust? 标签
            # 2.抓取画师关注的画师，如此循环，画师关系网
            ids_big = 'https://www.pixiv.net/ajax/user/{}/profile/illusts?'.format(painter_id)    # 这里的url拼接是按每48个算一页，来获取作品的id、title、url、tags 作品详细数据url
            # ids_big = 'https://www.pixiv.net/ajax/user/5375435/profile/illusts?'    # 这里的url拼接是按每48个算一页，来获取作品的id、title、url、tags 作品详细数据url
            for work_id in grouping_list:
                ids = 'ids%5B%5D=' + work_id + '&'
                ids_big = ids_big + ids 
            works_url = ids_big + 'work_category=illustManga&is_first_page=1'
            # works_url = ids_big + 'is_manga_top=0'
            count += 1
            # print('第%s页的works_url:%s' % (count,works_url))                        # 每页        
            works_html = self.request(works_url)
            works_json = json.loads(works_html.text)
            print(works_url)
            works_data = works_json["body"]["works"].values()    #作品详细数据 大集合    # print(works_json["body"]["works"].values())
            for x in works_json["body"]["works"].values():         #作品详细数据 大集合
                title = x['title']
                folder_id = x['id']
                # 返回作品id文件夹的路径
                folder_path = self.mkdir_works(folder_id)   #创建一个作品id+title的文件夹存放单图/多图/漫画   #如果存在则跳过
                tags = x['tags']
                small_url = x['url']
                pageCount = x['pageCount']
                print('\n作品标题:',x['title'])   #作品标题
                print('作品页数:',x['pageCount'])   #页数
                # folder_path = self.path + '\\'+ painter_id + '--' + name + '\\' + folder_id   #基本目录 + 画师id + 名字 + 作品id
                
                '''
                u = 'https://i.pximg.net/c/250x250_80_a2/img-master/img/2016/05/23/19/25/26/57027442_p0_square1200.jpg'
                r = r"(?<=/img/).+?(?=g)"
                p = re.compile(r)
                m = re.search(p,u)
                m.group()
                # 2016/05/23/19/25/26/57027442_p0_square1200.jp
                '''

                # 每个作品的详细信息
                # https://www.pixiv.net/ajax/illust/72059843

                if pageCount == 1:
                    if small_url[51:-15][-2:] == 'p0':
                        print('作品类型：单图\n')
                        single_graph += 1
                        self.img_single(small_url,folder_path,folder_id)
                    else:
                        print('作品类型：动图\n')
                        gif_graph += 1
                        self.img_gif(folder_path,folder_id)
                else:
                    print('作品类型：多图\n')
                    multi_graph += 1
                    self.img_multi(small_url,folder_path,folder_id,pageCount)
            # 每页作品获取完或检查完之后休眠5s
            # time.sleep(5)
        print('---------------------------')
        print('单图共:%s张' % (single_graph))
        print('多图共:%s张' % (multi_graph))
        print('动图共:%s张' % (gif_graph))        
        print('---------------------------')

    def mkdir_painter (self,painter_id,name):
        name = re.sub('[\/:*?"<>|]','_',name)
        folder_name = painter_id + '--' + name
        # 画师改名字！会导致重下
        for folder in os.listdir(self.path):
            if painter_id == folder.split('--')[0]:
                print(u'[名字叫{0}文件夹已存在！]'.format(folder_name))
                father_folder = os.path.join(self.path,folder)
                os.chdir(father_folder) ##切换到目录
                return father_folder

        print(u'[建了一个{0}文件夹！]'.format(folder_name))
        father_folder = os.path.join(self.path,folder_name)
        os.makedirs(father_folder)
        os.chdir(father_folder) ##切换到目录
        return father_folder


        # 0331 注释   
        # reason:画师名字更改，但id唯一，会引起文件夹重建，作品重下
        '''
        isExists = os.path.exists(os.path.join(self.path,folder_name))
        if not isExists:
            print(u'[建了一个{0}文件夹！]'.format(folder_name))
            os.makedirs(os.path.join(self.path,folder_name))
            os.chdir(os.path.join(self.path,folder_name)) ##切换到目录
            return True
        else:
            print(u'[名字叫{0}文件夹已存在！]'.format(folder_name))
            os.chdir(os.path.join(self.path,folder_name)) ##切换到目录
            return False
        '''
        # 0331 注释

    def mkdir_works(self,folder_id):
        folder_path = os.path.join(self.father_folder,folder_id)
        isExists = os.path.exists(folder_path)

        if not isExists:
            print(u'\n[在',self.father_folder,'下建了一个', folder_id, u'文件夹！]')
            os.makedirs(folder_path)
            os.chdir(folder_path) ##切换到目录
            return folder_path
        else:
            print(u'\n[在',self.father_folder,'下已经有', folder_id, u'文件夹！]')
            os.chdir(folder_path) ##切换到目录
            return folder_path

    def img_single(self,small_url,folder_path,folder_id):
        # print('当前目录',folder_path)
        work_name = folder_id + small_url[-4:]
        jpg_judge_path = folder_path + '\\' + work_name            #p站的图片有jpg和png的，但是从works_url获取到的只有小图jpg的url
        png_judge_path = folder_path + '\\' + folder_id + '.png'   #判断是否是上次因为jpg不行而下载png的图片，如果是的话，expand_name 用 .png 替换进行比对是否重复
        if os.path.exists(jpg_judge_path) == True and os.path.getsize(jpg_judge_path) != 58:   #判断jpg
            print(jpg_judge_path,'已存在且字节数不为58！')
        else:
            if os.path.exists(png_judge_path) == True and os.path.getsize(png_judge_path) != 58:   #判断png
                print(png_judge_path,'已存在且字节数不为58！')
            else:
                try:
                    # small_date = small_url[51:-15]  #动图的small_url没有p0
                    r = r'''.*?([0-9]{4}/[0-9]{2}/.*?_p).*?'''
                    p = re.compile(r)
                    small_date = re.findall(p,small_url)[0]

                    head = 'https://i.pximg.net/img-original/img/'
                    img_url = head + small_date + str(0) + small_url[-4:]        #.jpg
                    img_html = self.request(img_url)
                    # print(img_url)
                    size = self.down(img_html,work_name,jpg_judge_path)
                    # time.sleep(2)
                    if size == 58:
                        time.sleep(3)
                        print('{}格式不对，准备重下'.format(work_name))
                        img_url = head + small_date + str(0) + '.png'
                        img_html = self.request(img_url)
                        self.down_conversion(img_html,folder_id,jpg_judge_path,png_judge_path)
                        # print('下载图片的字节数为：',os.path.getsize(png_judge_path))
                    # else:
                        # print('下载图片的字节数为：',os.path.getsize(jpg_judge_path))
                except:
                    print(img_url)
                    print(work_name,'下载失败')

    def img_multi(self,small_url,folder_path,folder_id,pageCount):
        # print('当前目录',folder_path)
        for img_num in range(0,pageCount):
            work_name = folder_id + '-' + str(img_num) + small_url[-4:]       
            jpg_judge_path = folder_path + '\\' + work_name
            png_judge_path = folder_path + '\\' + folder_id + '-' + str(img_num) + '.png'
            if os.path.exists(jpg_judge_path) == True and os.path.getsize(jpg_judge_path) != 58:
                print(jpg_judge_path,'已存在且字节数不为58！')
                if os.path.exists(png_judge_path) == True and os.path.getsize(png_judge_path) != 58:   #判断png
                    print(png_judge_path,'已存在且字节数不为58！')
                else:
                    # 2019.11.01
                    # multi_url = 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=' +folder_id + '&page=' + str(img_num)
                    # self.headers['User-Agent'] = random.choice(self.user_agent_list)
                    try:
                        # 2019.11.01
                        # multi_html = self.request(multi_url)
                        # multi_html_soup = BeautifulSoup(multi_html.text, 'lxml')
                        # img_url = multi_html_soup.find('img')['src']     #要请求src的地址再写入

                        # small_date = small_url[51:-16]  #动图的small_url没有p0
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

    def img_gif(self,folder_path,folder_id):
        # print('当前目录',folder_path)
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
            # imageio.mimsave(gif_name, frames, 'GIF', fps = 24)  # 合成gif
            imageio.mimsave(gif_name, frames, 'GIF', fps  = delay) # 间隔
            # print(folder_id,'动图下载完成！')
            print('%s 完成\t大小为%.2f'%(gif_name,os.path.getsize(gif_judge_path)/float(1024*1024)))
            for file in files:
                os.remove(file)

    def down(self,img_html,work_name,jpg_judge_path):
        f = open(work_name, 'wb')
        f.write(img_html.content)   
        f.close()
        # print('{}完成\t大小为{}Mb'.format(work_name,os.path.getsize(jpg_judge_path)/float(1024*1024)))
        print('%s完成\t大小为%.2f'%(work_name,os.path.getsize(jpg_judge_path)/float(1024*1024)))
        return os.path.getsize(jpg_judge_path)

    def down_conversion(self,img_html,folder_id,jpg_judge_path,png_judge_path,img_num=None):
        if os.path.exists(jpg_judge_path) == True:
            # print('格式错误的文件已找到')
            os.remove(jpg_judge_path)
            print('格式错误的文件已删除')
        if img_num == None:
            work_name = folder_id + '.png'
        else:
            work_name = folder_id + '-' + str(img_num) + '.png'
        f = open(work_name, 'wb')
        f.write(img_html.content)
        f.close()
        # print(work_name + '已转换格式下载完成')
        # print('{}完成\t大小为{}'.format(work_name,os.path.getsize(png_judge_path)/float(1024*1024)))
        print('%s完成\t大小为%.2f'%(work_name,os.path.getsize(png_judge_path)/float(1024*1024)))

    def request(self,url,num_entries = 7):
        try:                              #为了检查可用ip的数量，但是现在使用ip.seofangfa.com,暂时注释
            proxy_ip = random.choice(self.agent_ip_list)
            proxies = {'http': 'http://'+ proxy_ip,
                        'https': 'https://'+proxy_ip}
            # print('代理ip:%s\n' % (proxy_ip))               # proxies=proxies
            content = se.get(url, headers=self.headers,cookies=self.jar,verify=False,timeout=15)
            return content                                              
        except:
            print('error...')
            if num_entries > 0:
                # 现在用不到代理，暂时不做操作
                # self.agent_ip_list.remove(proxy_ip)
                # self.error_ip_list.append(proxy_ip)
                self.check_agentlist()
                print('剩余重试次数:%s' % (num_entries))
                return self.request(url,num_entries = num_entries - 1)
            else:
                print('代理无效或网络错误')

    def check_agentlist(self):      # #为了检查可用ip的数量，但是现在使用ip.seofangfa.com,暂时注释
        print('\n代理池总量:',len(self.agent_ip_list))
        if len(self.agent_ip_list) < 0:
            print('代理池总量低于阈值...')
            self.Agent()
        else:
            print('代理池总量不低于阈值...')
            return True

    def Agent(self):       #收集ip        #从89代理上收集,太不稳定了
        print('正在搜索代理ip...')
        ip_agent_url = 'https://proxy.seofangfa.com/'
        # ip_agent_url = 'https://www.xicidaili.com/nn/'
        html = requests.get(url=ip_agent_url,headers=self.headers,verify=False,timeout=5)
        
        html_soup = BeautifulSoup(html.text, 'lxml')
        ip_list = html_soup.find('tbody').find_all('tr')[26:]    #去除第一个和前25个，26-50为国外ip
        # ip_list = html_soup.find('tbody').find_all('tr')[1:26]    #去除第一个和前25个，26-50为国外ip
        items = []
        print('搜索完成,代理信息如下:') 
        for item in ip_list:        # list(ip_port)[0]为ip,[1]为端口,[2]响应时间,[3]位置,[4]最后验证时间
            ip_port = list(item)[0].get_text() + ':' +list(item)[1].get_text()
            print('ip: %s ,响应时间: %ss ,ip位置: %s' % (ip_port,list(item)[2].get_text(),list(item)[3].get_text()))
            items.append(ip_port)        #存储爬取到的ip(需要添加)
        self.save_ip(items)
    
    def save_ip(self,items):
        # items = ['92.255.255.78:54628','54.252.210.83:80','118.136.25.116:8080',
        #         '54.214.177.201:8888','178.62.249.43:53281','110.170.184.61:8080',
        #         '36.65.182.191:8080','182.53.197.223:8080','194.44.138.48:53281',
        #         '110.170.184.61:8080','103.245.19.69:56737','95.159.106.249:45259',
        #         '82.209.217.214:8080','139.255.92.234:57269','177.91.254.116:8080',
        #         '202.137.10.179:57338','176.60.208.30:49099','182.53.206.178:8080',
        #         '95.159.106.249:45259','212.154.58.101:34416','109.251.252.123:50171',
        #         '94.242.57.136:10010','212.154.58.109:34416','164.77.134.10:8080','179.127.242.60:8080']
        print('\n正在写入...')
        lines = self.read_txt()
        # print(len(lines))
        f = open('0131_pixiv.txt','a+')
        for item_num in range(0,len(items)):
            if items[item_num] in lines:      #进行判断
                pass
            else:
                f.write(items[item_num])                #写入
                f.write('\n')
        f.close()
        count_line = 0                                      #输出行数，可有可无
        for index,line in enumerate(open('0131_pixiv.txt','r')):
            count_line += 1
        print('写入完成!\n当前行数:',count_line)
        # 可以考虑将可用ip存入
        self.judge()

    def judge(self):       # 检验ip活性     # https://ip.seofangfa.com/
        print('正在进行代理池ip活性检测......\n')
        judge_list = self.read_txt()
        for judge in judge_list[:10]:
            self.agent_ip_list.append(judge)    # 暂时跳过校验
            '''
            if judge in self.error_ip_list:
                print(judge,'无效')
            else:
                if judge in self.agent_ip_list:
                        print(judge,'已在代理池中...')
                else:
                    proxy = {
                            'http':judge,
                            'https':judge}
                    judge_url = 'https://www.baidu.com/'     #遍历时，利用访问百度，设定timeout=1,即在1秒内，未送到响应就断开连接
                    # judge_url = 'https://www.pixiv.net/'     #遍历时，利用访问百度，设定timeout=1,即在1秒内，未送到响应就断开连接
                    try:
                        response = requests.get(url=judge_url,headers=self.headers,proxies=proxy,verify=False,timeout=5)
                    except:
                        print(judge,'不可用...')
                        self.error_ip_list.append(judge)
                    else:
                        self.agent_ip_list.append(judge)
                        print(judge,'可用...')
                        '''
        print('代理池ip活性检测完毕...\n代理池总量:',len(self.agent_ip_list),'\n代理池:',self.agent_ip_list)

    def read_txt(self):
        path = u'H:\\'
        lines = []
        os.chdir(path)
        # print(os.getcwd())
        for index,line in enumerate(open('0131_pixiv.txt','r')):        #获取文本内容
            lines.append(line.replace('\n',''))
        return lines
    
    def work(self):
        self.Agent()
        print('开始模拟登陆...')
        self.jar = self.new_login()
        # self.login()
        self.attention_html()
        
pixiv = Pixiv()
pixiv.work()
    # 爬取ip过程 ： tbody,从第一个tr开始(第0个除外)到最后一个,利用循环,选择tr中的第一个td(ip)和第二个td(td)
    # proxy_list = ['xxx.xxx.xxx.xxx:xxx']
    # 然后从proxy_list中随机选出一个proxy(ip+':'+port)进行验证,访问百度响应状态码200则通过,不行则回滚重新选择ip
    # 设置proxies的格式:
    # proxies = {'http':'http://'+proxy,'https':'https://+proxy'}


    # for file in files:              #jpg->png
            #     name = os.getcwd() + '\\' + file          #PIL转换格式需要用到
            #     png_name = file[:-4]+'.png' #png名字
            #     im = Image.open(name)
            #     width_pixel = im.size[0]/2  #/2gif是10M左右
            #     high_pixel = im.size[1]/2   #im.size 是 tuple类型
            #     size = width_pixel,high_pixel
            #     im.thumbnail((size))
            #     im.save(png_name)           #转换
            #     image_list.append(png_name)
            #     os.remove(name)             #删除jpg 
            # print('格式转换完毕')         # print(image_list,delay,gif_name)