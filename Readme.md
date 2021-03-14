# PixiC V2.1.5 2021/03/14

---

**PixiC是一个专注于Pixiv个人插画下载和数据收集的Python爬虫**

+ 通过Selenium持久化cookie或用户自定义cookie从而绕过Google Recaptcha V3验证；
+ 通过scheduler模块调度各个插件模块（关注模块、收藏模块、API模块）进行定时任务

</br>

## 使用方法

---

部署文档见  [wiki](https://github.com/Coder-Sakura/PixiC/wiki)(推荐) 或 [Blog](http://00102400.xyz/blog/2020/06/24/pixic-bu-shu/)

API文档：[wiki](https://github.com/Coder-Sakura/PixiC/wiki/API文档) 或 [Blog](http://00102400.xyz/blog/2020/07/08/pixicapi/)，[运行截图](https://github.com/Coder-Sakura/PixiC/wiki/运行截图)在wiki也有展示



## 1、PixiC目前支持功能：

支持获取Chrome浏览器上登录的Pixiv账户cookie并持久化

- [x] 支持用户自定义cookie池(单个或多个cookie)
- [x] **支持单图、多图、动图的原图下载**
- [x] **支持下载账号关注用户的作品和数据入库**
- [x] **支持下载账号收藏作品**
- [x] 支持设置收藏限制数以进行筛选下载
- [x] 支持数据库开关以决定是否使用数据库
- [x] 支持API：查询pid信息接口、随机插画接口 (提供反代直连链接)
- [ ] 日榜、周榜、月榜 



## 2、基本使用

请参考**使用方法**的<部署文档>完成环境搭建和依赖安装，接着运行

```
python scheduler.py
```



## 3、关于PixiC与qq机器人

目前使用Flask + go-cqhttp + PixiC可实现随机涩图、查询指定pid信息等机器人功能。

效果如下，机器人还未开源出来，除了对接PixiC API还有其他功能，敬请期待吧。

+ 查询pid

![](https://i.loli.net/2021/01/02/PH2NnqUpZBCwo6c.png)

+ 随机插画

![](https://i.loli.net/2021/01/02/1XUNKrsnJRk6V95.png)



## 写在结尾的话

---

+ 之前存在一个V1.0版本，不过结构简单、功能也不多，后面准备关注画师作品下载和收藏下载功能单独做出来，后续会放到[Tools](https://github.com/WriteCode-ChangeWorld/Tools)上。
+ **现在的V2.0版本更健壮，功能更多。旨在简单配置后，敲下回车即能获取到Pixiv账号的数据和作品**
+ 个人技术能力有限，欢迎反馈 bug 和提出建议。