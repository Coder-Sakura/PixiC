# coding=utf8
"""
输出模板
time: 2020-05-29
author: coder_sakura
"""

VERSION = "v2.1.11"
# ================================================
TEMP_MSG = {
	"VERSION_INFO": "==========PixiC-{}==========".format(VERSION),
	# db
	"DB_INFO": "使用API需要开启数据库",
	"DB_CONNECT_ERROR_INFO": "请确保数据库打开并运行或重新检查数据库配置\n{}",
	"DB_INST": "{}:数据库连接池实例化",
	"DB_UPDATE_ILLUST_ERROR_INFO": "{}:更新作品:{},出错:{}",

	# Login
	"LOGIN_ERROR_INFO": "{}:请打开代理软件或先使用Chrome登录Pixiv",
	"INIT_INFO": "{}:初始化完成!",
	"COOKIE_EMPTY_INFO": "{}:本地Cookie为空,请更新",
	"FILE_NOT_FOUND_INFO_1": "{}:pixiv_cookie文件不存在",
	"FILE_NOT_FOUND_INFO_2": "{}:首次运行请将config文件中的COOKIE_UPDATE_ENABLED设置为True",
	"CONVERT_COOKIEJAR_ERROR_INFO": "{}:自定义cookie转换失败! 请检查或重新粘贴cookie",
	"GET_COOKIE_INFO": "{}:正在获取账号信息",
	"GET_COOKIE_NOW_INFO": "{}:获取信息时请关闭Chrome",
	"GOOGLE_CAPTCHA_ERROR_INFO": "{}:请检查cookie是否有效或将config文件的COOKIE_UPDATE_ENABLED设置为True",

	# CW
	"BEGIN_INFO": "{}:开始轮询",
	"SLEEP_INFO": "{}:进入休眠",
	"FOLLOW_SUCCESS_INFO": "{}:成功获取关注列表.共{}位关注用户",
	"FOLLOW_ERROR_INFO": "{}:获取关注列表出错",
	"FOLLOW_PAGE_ERROR_INFO": "{}:获取画师出错,第{}-{}位",
	"FOLLOW_NO_ILLUSTS_INFO": "{}:{}(uid:{})无作品",
	"FOLLOW_DATA_ERROR_INFO": "{}:获取画师数据出错 {}",
	"UPDATE_USER_INFO": "{}:{}更新画师:{}(uid:{}) | 作品数:{} 最新作品:{}",
	"NOW_USER_INFO": "{}:{}当前画师:{}(uid:{}) |作品数: {}",
	"NO_FOLLOW_USERS": "{}:关注列表为空",
	"DELELE_USER_ILLUST_SUCCESS_INFO": "{}:删除画师作品记录成功:{}(uid:{}) | 该画师在pixiv已无作品",
	"DELELE_USER_ILLUST_FAIL_INFO": "{}:删除画师作品记录失败:{}(uid:{}) | 该画师在pixiv已无作品",
	"USER_LEAVE_PIXIV_INFO_CN": "您当前所寻找的个用户已经离开了pixiv",

	# BM
	"BOOKMARK_PAGE_ERROR_INFO": "{}:获取收藏出错: 第{}-{}张失败",
	"BOOKMARK_PAGE_EMPTY_INFO": "{}:当前收藏: 第{}-{}张为空",
	"BOOKMARK_NOW_INFO": "Pixiv收藏作品第{}-{}张获取成功,共{}张可用",
	"UPDATE_INFO": "{}:进行更新",
	"UPDATE_CANLE_INFO": "{}:暂不更新",
	"UPDATE_CHECK_ERROR_INFO": "{}:检查更新出错!",
	"UPDATE_CHECK_EMPTY_INFO": "{}:公开/未公开收藏均为空,暂不更新",
	"UPDATE_CHECK_NO_AUTH_INFO": "{}:\n当前使用的< pixiv_cookie内的账号信息 >与< 要获取的未公开收藏的账号(uid:{}) >不是同一个!"\
								"\n如需继续获取该账号(uid:{})的未公开收藏,请按以下步骤操作:\n1. 备份并删除pixiv_cookie"\
								"\n2. 将config.py中的COOKIE_UPDATE_ENABLED设置为True\n3. 在chrome上登录对应的pixiv账号"\
								"\n4. 重新运行PixiC即可."\
								"\n\n取消获取该账号的未公开收藏,将BOOKMARK_HIDE_ENABLE设置为False即可",
	"UPDATE_DAY_LIMIT_INFO": "{}:达到每日更新量:{}张,当前位于周期更新第{}天",
	"UPDATE_DAY_ALL_INFO": "{}:已对所有收藏作品进行全更新,day_count将清零",
	"NO_AUTH" : "没有权限",

	# 线程函数通用
	"ILLUST_NETWORK_ERROR_INFO": "{}:PID:<{}>请求错误,{}",
	"ILLUST_EMPTY_INFO": "{}:该作品{}已被删除,或作品ID不存在,或被限制访问",
	"INSERT_SUCCESS_INFO": "{}:插入{}成功",
	"INSERT_FAIL_INFO": "{}:插入{}失败",
	"DELELE_ILLUST_SUCCESS_INFO": "{}:已删除{}作品记录 | pixiv上不存在该作品/作品已删除/作品已设为私密",
	"DELELE_ILLUST_FAIL_INFO": "{}:删除{}作品记录失败 | pixiv上不存在该作品/作品已删除/作品已设为私密",

	# DM
	"DM_NETWORK_ERROR_INFO": "{}:代理无效/网络错误,options:{} | exception:{}",
	"DM_RETRY_INFO": "尝试重新请求:{}",
	"DM_DOWNLOAD_SUCCESS_INFO": "{}:{}下载成功!大小:{}",
	"UNLOGIN_TEXT": "出现了未知错误",
	"UNLOGIN_INFO": "{}:请先在Chrome上登录Pixiv账号",
	"UL_TEXT": "UNLOGIN",
	"PID_DELETED_TEXT": "该作品已被删除, 或作品ID不存在。",
	"PID_ERROR_TEXT": "无法找到您所请求的页面",
	"PID_UNAUTH_ACCESS": "作者已设置为私密,尚无权限浏览该作品",
	"PID_UNAUTH_ACCESS_2": "尚无权限浏览该作品",
	"LIMIT_TEXT": "出现错误。请稍后再试。",
	"LIMIT_TEXT_RESP": "请求太快被限制访问,休眠一段时间后恢复访问<{}>",
	"JSON_DECODE_ERR": "Json数据解析失败 - {}",

	# API
	# 查询不到数据
	"NO_DATA_MESSAGE": "There Is No Data Corresponding To This Pid - {}",
	# 没有该标签的作品
	"NO_TAG_MESSAGE": "There Is No Illusts Corresponding To The Tag",
	# 参数错误
	"PARAM_ERROR": "Params <{}> Error - {},Try Again",
	# 内部错误
	"INTERNAL_ERROR_MESSAGE": "Internal Error - <{}> - {}",
	# API地址错误
	"API_ADD_ERROR": "请检查API地址!",
	# 500错误
	"API_ERROR": "服务器出错,请参考日志输出",
	"API_RANDOM_LEVEL_LIST": ['R','SR','SSR','UR'],

	### TAG COUNT
	"TAG_TASK_START": "{}:tag统计进程开始工作",
	"TAG_TASK_END": "{}:tag统计进程结束工作",

}
# ================================================
