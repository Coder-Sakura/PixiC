# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
# from lxml import etree

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
from requests.exceptions import *
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

def log_str(*args):
    for i in args:
        now_time = time.strftime("%Y-%m-%d %H:%M:%S")
        print('{} {}'.format(now_time,i))


class Pixiv():
    def __init__(self):
        self.headers = {
            "Connection": "keep-alive",
            'referer': 'https://www.pixiv.net/',
            'origin': 'https://accounts.pixiv.net',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            # 'cookie':'first_visit_datetime_pc=2019-06-30+14%3A02%3A10; p_ab_id=7; p_ab_id_2=2; p_ab_d_id=1741459444; _ga=GA1.2.1541262787.1560534037; privacy_policy_agreement=1; c_type=20; a_type=0; b_type=0; module_orders_mypage=%5B%7B%22name%22%3A%22sketch_live%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22tag_follow%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22recommended_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22everyone_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22following_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22mypixiv_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22spotlight%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22fanbox%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22featured_tags%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22contests%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22user_events%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22sensei_courses%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22booth_follow_items%22%2C%22visible%22%3Atrue%7D%5D; yuid_b=KSKZB1M; login_ever=yes; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^6=user_id=27858363=1^9=p_ab_id=7=1^10=p_ab_id_2=2=1^11=lang=zh=1; ki_r=; __utmz=235335808.1561936687.5.3.utmcsr=pixiv.help|utmccn=(referral)|utmcmd=referral|utmcct=/hc/zh-tw; limited_ads=%7B%22responsive%22%3A%22%22%7D; categorized_tags=3ze0RLmk59~6sZKldb07K~HLWLeyYOUF~OT-C6ubi9i~jfnUZgnpFl; tag_view_ranking=jfnUZgnpFl~SQZaakhtVv~uW5495Nhg-~DHqIUplIEc~b3tIEUsHql~Lt-oEicbBr~RTJMXD26Ak~GF09UjQt_e~gVfGX_rH_Y~jH0uD88V6F~kwQ7-a01CG~-fP8ij-3EX~3W4zqr4Xlx~kGYw4gQ11Z~MSNRmMUDgC~8ch4HlASni~Cj_Gcw9KR1~kW8varCrdB~1yIPTg75Rl~NIpEilHR4P~5oPIfUbtd6~OYl5wlor4w~NNraL54MQl~eYIfp1VgVQ~U9A9K0M8Oi; p_b_type=1; device_token=205af45342716361b4dff3fde8e51c15; is_sensei_service_user=1; _gid=GA1.2.1295270473.1565421992; __utmc=235335808; tags_sended=1; login_bc=1; ki_t=1561871297792%3B1565423294286%3B1565423294286%3B4%3B16; __utma=235335808.988886957.1561870925.1565421994.1565426875.15; __utmt=1; __utmb=235335808.1.10.1565426875; _gat=1; PHPSESSID=27858363_050406b681a63254195a7d8484a6a4d8'
            }
        self.pixiv_user_id = ''
        self.jar = RequestsCookieJar()
        self.path = 'H:\se18'
        self.father_folder = ''

        # 关注画师的获取
        self.follw_url = "https://www.pixiv.net/ajax/user/{}/following"
        self.offset = 0
        self.fix_value = 24
        # 画师所有作品
        self.user_illusts_url = "https://www.pixiv.net/ajax/user/{}/profile/all"

    def get_cookie(self):
        pro_dir = r'C:\Users\Hatsune Miku\AppData\Local\Google\Chrome\User Data'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        # chrome_options.add_argument('--disable-infobars') #disable the automation prompt bar
        chrome_options.add_argument('user-data-dir='+os.path.abspath(pro_dir))
        
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('https://www.pixiv.net/')
        # pixiv.user.id
        self.pixiv_user_id = self.get_user_id(driver.page_source)
        self.follw_url = self.follw_url.format(self.pixiv_user_id)
        # cookies
        cookies = driver.get_cookies()
        driver.quit()
        
        with open("pixiv_cookies", "w") as fp:  # 不直接利用,存下来保存比较好
            json.dump(cookies, fp)

        jar = self.set_cookie()
        if jar == []:
            print("请使用Chrome浏览器进行登录,以便获取cookie")
            print("请打开代理软件")
            exit()

        self.jar = jar
        return jar

    def get_user_id(self,page_source):
        '''
        返回登录用户的id
        '''
        user_id = re.findall(r'''.*?pixiv.user.id="(.*?)";.*?''',page_source.replace(" ",""))[0]
        return user_id

    def set_cookie(self):
        '''
        读取cookie
        '''
        jar = RequestsCookieJar()
        with open("pixiv_cookies", "r") as fp:
            cookies = json.load(fp)
            for cookie in cookies:
                jar.set(cookie['name'], cookie['value'])
        return jar

    def base_request(self,options,data=None,params=None,retry_num = 5):
        '''
        :params options 请求参数    {"method":"get/post","url":"example.com"}
        :params data
        :params params
        :params retry_num 重试次数
        :return response对象/False
        如果options中有定义了headers参数,则使用定义的;否则使用init中初始化的headers

        下面这行列表推导式作用在于：
        添加referer时,referer需要是上一个页面的url,比如:画师/作品页面的url时,则可以自定义请求头
        demo如下:
        demo_headers = self.headers.copy()
        demo_headers['referer']  = 'www.example.com'
        options ={
            "method":"get",
            "url":"origin_url",
            "headers":demo_headers
        }
        base_request(options=options)
        这样base_requests中使用的headers则是定制化的headers,而非init中初始化的默认headers了
        '''
        base_headers = [options['headers'] if 'headers' in options.keys() else self.headers][0]
        try:
            response = requests.request(
                    options["method"],
                    options["url"],
                    data = data,
                    params = params,
                    cookies = self.jar,
                    headers = base_headers,
                    verify=False,
                    timeout = 15,
                )
            return response
        except Exception as e:
        # except [TimeoutError,RequestException] as e:
            if retry_num > 0:
                return self.base_request(options,data,params,retry_num-1)
            else:
                print(e)
                print("代理无效或网络错误")
                # return False
    
    def get_page_users(self,offset):
        '''
        :params offset 偏移量
        '''
        params = {
            "offset":offset,
            "limit":self.fix_value,
            "rest":"show"
        }
        resp = self.base_request(options={"method":"get","url":self.follw_url}, params=params)
        # resp = se.get(self.follw_url,headers=self.headers.copy(),cookies=self.jar,verify=False,timeout=15).text
        users_list = json.loads(resp.text)
        # print(users_list,self.follw_url)
        return users_list

    def get_all_users(self):
        '''
        获取关注所有关注画师信息,包括uid,author,latest_pid
        '''
        offset = self.offset
        follow_page = 1
        users_info_list = []

        while True:
            users_list = self.get_page_users(offset)['body']['users']            

            for user in users_list:
                user_info = {}
                user_info["uid"] = user["userId"]
                user_info["userName"] = user["userName"]
                user_info["latest_pid"] = user["illusts"][0]["illustId"]
                users_info_list.append(user_info)
                offset += 1
                log_str("第%s页第%s位画师" % (follow_page,offset))

            follow_page += 1
            # offser += 24 
            if len(users_list) == 24:
                log_str('ok')
            else:
                log_str(len(users_list))
                break
        # print(users_info_list,len(users_info_list))
        return users_info_list

    def get_user_illusts(self,uid):
        '''
        用户所有作品字段说明:
        illusts:普通作品,单图动图多图都在这
        manga:漫画类作品
        novels:小说,不考虑
        mangaSeries:漫画系列,manga包含其中漫画系列的所有作品
        novelSeries:小说系列,不考虑
        综上,和以前一样,获取illusts和manga中的所有id
        '''
        user_illusts_url = self.user_illusts_url.format(uid)
        log_str(user_illusts_url)
        user_illusts = self.base_request(options={"method":"get","url":user_illusts_url}).text
        user_illusts_json = json.loads(user_illusts)['body']
        log_str(len(user_illusts_json['illusts']),len(user_illusts_json['manga']))
        # log_str(len(user_illusts_json['illusts']),len(user_illusts_json['manga']),len(user_illusts_json['novels'])
        #             ,len(user_illusts_json['mangaSeries']),len(user_illusts_json['novelSeries']))
        # log_str(len(user_illusts_json['manga']))
        # log_str(len(user_illusts_json['novels']))
        # log_str(len(user_illusts_json['mangaSeries']))
        # log_str(len(user_illusts_json['novelSeries']))




    def main(self):
        self.get_cookie()
        users_info_list = self.get_all_users()
        for user_info in users_info_list:
            self.get_user_illusts(user_info['uid'])
            # print()

    def attention_html(self):       # 获取关注画师界面的各种信息
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
        try:
            content = se.get(url, headers=self.headers,cookies=self.jar,verify=False,timeout=15)
            return content                                              
        except:
            print('error...')
            if num_entries > 0:
                print('剩余重试次数:%s' % (num_entries))
                return self.request(url,num_entries = num_entries - 1)
            else:
                print('代理无效或网络错误')
                # 记录错误日志
    
    def work(self):
        self.Agent()
        print('开始模拟登陆...')
        self.jar = self.get_cookie()
        # self.login()
        self.attention_html()
        
pixiv = Pixiv()
pixiv.main()
# pixiv.get_cookie()
# pixiv.get_all_users()