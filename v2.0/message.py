# coding=utf8
"""
输出模板
time: 2020-05-29
author: coder_sakura
"""

# ================================================
# db
DB_INFO = "使用API需要开启数据库"
DB_CONNECT_ERROR_INFO = "请确保Mysql在运行/配置好\n{}"
DB_INST = "数据库连接池实例化"
DB_UPDATE_ILLUST_ERROR_INFO = "{}:更新作品:{},出错:{}"

# Login
LOGIN_ERROR_INFO = "{}:打开代理软件/使用Chrome登录Pixiv"
INIT_INFO = "{}:初始化完成！"
COOKIE_EMPTY_INFO = "{}:本地Cookie为空,请更新"
FILE_NOT_FOUND_INFO = "{}:首次运行请将COOKIE_UPDATE_ENABLED设置为True"
GET_COOKIE_INFO = "{}:正在获取账号信息"
GET_COOKIE_NOW_INFO = "{}:获取信息时请关闭Chrome"

# CW
BEGIN_INFO = "{}:开始轮询"
SLEEP_INFO = "{}:进入休眠"
FOLLOW_SUCCESS_INFO = "{}:成功获取关注列表.共{}位关注用户"
FOLLOW_ERROR_INFO = "{}:获取关注列表出错"
FOLLOW_PAGE_ERROR_INFO = "{}:获取画师出错,第{}-{}位"
FOLLOW_NO_ILLUSTS_INFO = "{}:{}无作品"
FOLLOW_DATA_ERROR_INFO = "{}:获取画师数据出错 {}"
UPDATE_USER_INFO = "{}:更新画师:{}(pid:{}) | 作品数:{} 最新作品:{}"
NOW_USER_INFO = "{}:当前画师:{}(pid:{}) |作品数: {}"

# BM
BOOKMARK_PAGE_ERROR_INFO = "{}:获取收藏出错: 第{}-{}张失败"
BOOKMARK_NOW_INFO = "{}:当前收藏:第{}-{}张获取成功,共{}张可用"
UPDATE_INFO = "{}:进行更新"
UPDATE_CANLE_INFO = "{}:暂不更新"
UPDATE_CHECK_ERROR_INFO = "{}:检查更新出错!"

# 线程函数通用
ILLUST_NETWORK_ERROR_INFO = "{}:{}请求错误,{}"
ILLUST_EMPTY_INFO = "{}:该作品{}已被删除,或作品ID不存在"
INSERT_SUCCESS_INFO = "{}:插入{}成功"
INSERT_FAIL_INFO = "{}:插入{}失败"

# DM
DM_NETWORK_ERROR_INFO = "{}:代理无效/网络错误,{}\n{}"
DM_DOWNLOAD_SUCCESS_INFO = "{}:{}下载成功!大小:{}"
UNLOGIN_TEXT = "出现了未知错误"
UNLOGIN_INFO = "{}:请先在Chrome上登录Pixiv账号"

# API
# 查询不到数据
NO_DATA_MESSAGE = "There Is No Data Corresponding To This Pid"
# 没有该标签的作品
NO_TAG_MESSAGE = "There Is No Illusts Corresponding To The Tag"
# 参数错误
PARAM_ERROR = "Params Error,Try Again"
# 内部错误
INTERNAL_ERROR_MESSAGE = "Internal Error"
# API地址错误
API_ADD_ERROR = "请检查API地址!"
# 500错误
API_ERROR = "出错了"
# ================================================
