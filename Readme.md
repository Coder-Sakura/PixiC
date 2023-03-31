<div align="center">

# PixiC V2.1.7

## **一个专注于 [PIXIV](https://www.pixiv.net/) 收藏插画和关注画师数据收集的Python爬虫**

</div>

</br>

**推荐旧版本用户升级到v2.1.7以上的版本**

</br>

## 1、功能

---

**当前支持功能**

- [x] **支持获取Chrome浏览器登录的Pixiv账户并生成cookie文件持久化**（新设备直接使用该文件即可）
- [x] **支持单图、多图、动图的原图下载**
- [x] **支持指定uid用户的关注画师作品的下载与数据收集**
- [x] **支持指定uid用户的公开/未公开收藏作品的下载与数据收集**
- [x] 支持周期性轮询以应对pixiv限制访问机制
- [x] 提供作品下载最低收藏数限制 --> [传送门](https://github.com/Coder-Sakura/PixiC/wiki/%E5%85%B3%E4%BA%8EPixiC%E9%85%8D%E7%BD%AE%E7%9A%84%E4%B8%89%E8%A8%80%E4%B8%A4%E8%AF%AD#%E5%87%A0%E7%A7%8D%E5%B8%B8%E8%A7%81%E5%9C%BA%E6%99%AF%E7%9A%84config%E6%96%87%E4%BB%B6%E9%85%8D%E7%BD%AE)
- [x] 提供pixiv作品稀有度划分 --> [传送门](https://github.com/Coder-Sakura/PixiC/wiki/%E5%85%B3%E4%BA%8EPixiC%E7%9A%84%E6%9D%82%E8%B0%88#%E5%85%B3%E4%BA%8E%E4%BD%9C%E5%93%81%E7%A8%80%E6%9C%89%E5%BA%A6%E5%88%92%E5%88%86)
- [x] 提供API以查询pid信息、随机插画接口 (含反代链接)
- [x] 可通过用户自定义cookie池(单个或多个cookie)
- [x] 可通过数据库开关以决定是否使用数据库收集数据
- [x] 日志功能

</br>

TODO list

- [ ] 日榜、周榜、月榜 
- [ ] 线程级任务状态通知用户（server酱、邮件等）

</br>

## 2、基本使用

---

+ 部署文档：  [WIKI](https://github.com/Coder-Sakura/PixiC/wiki) (推荐) 或 [Blog](http://mybot.top/blog/2020/06/24/pixic-bu-shu/)
+ 运行截图戳这：[运行截图](https://github.com/Coder-Sakura/PixiC/wiki/运行截图)
+ 注意事项戳这：[注意事项](https://github.com/Coder-Sakura/PixiC/wiki/%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9)

</br>

请参考<部署文档>完成环境搭建和依赖安装，接着运行

```
python scheduler.py
```

</br>

## 3、用途展示

---

### 随机pixiv插画

> PixiC API + [Mybot机器人](https://github.com/WriteCode-ChangeWorld/mybot)或其他qq机器人 可实现<请求API获取随机pixiv插画>

> Mybot现正处于开发阶段，欢迎star和fork

+ 查询pid

![](https://i.loli.net/2021/01/02/PH2NnqUpZBCwo6c.png)

+ 随机插画

![](https://i.loli.net/2021/01/02/1XUNKrsnJRk6V95.png)



### 阅读3.0 订阅源

订阅源链接: [蓝奏云](https://python.lanzout.com/b0bsanjmj)  密码: hsvs

![](https://s2.loli.net/2022/01/21/2Nh9r8gRYeSI5s4.jpg)



## 结尾的话

---

+ 希望可以提交`issue`和`pr`来帮助本项目进行完善，也欢迎`fork`和`star`本项目以对作者表示支持，感谢！
+ 本仓库仅用于学习与交流使用，因使用而产生的一切纠纷与原作者无关。