pass

from login import Login
from config import COOKIE_UPDATE_ENABLED,ROOT_PATH
from folder import Folder


if __name__ == '__main__':
    # # 登录测试案例
    # jar = Login().cookie
    # # print(jar)
    # import requests
    # url = 'https://www.pixiv.net/bookmark.php?type=user'
    # headers = {
    #     'referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    #     'origin': 'https://accounts.pixiv.net',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
    #                   'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    # if '灼热' in requests.get(url,headers=headers,cookies=jar).text:
    #     print('ok')
    # exit()

    folder = Folder()

    # cookie = Login().cookie
    painter_path = folder.mkdir_painter('200066','陰 祭')
    for i in range(10):
        i = folder.mkdir_illusts(painter_path,i)
        print(i)


    # f_path = folder.mkdir_painter('200066','陰 祭')
    # folder.mkdir_works(f_path,'76822011')
    # print('over')