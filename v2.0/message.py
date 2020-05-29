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
DM_DOWNLOAD_SUCCESS_INFO = "{}:下载成功!大小:{}"
# ================================================
