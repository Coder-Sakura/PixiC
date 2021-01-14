**PixiC V2.1.4**

+ 部署文档： [Wiki](https://github.com/Coder-Sakura/PixiC/wiki),  [Blog](http://00102400.xyz/blog/2020/06/24/pixic-bu-shu/)
+ API文档：[API](https://github.com/Coder-Sakura/PixiC/wiki/API文档),  [Blog](http://00102400.xyz/blog/2020/07/08/pixicapi/)
+ Wiki：[Wiki](https://github.com/Coder-Sakura/PixiC/wiki)
+ [运行截图](https://github.com/Coder-Sakura/PixiC/wiki/运行截图)戳这里



**1、PixiC目前实现功能：**

- [x] 获取Pixiv登录信息：获取Chrome的Pixiv账户信息和用户自定义单/多个cookie
- [x] 支持单图、多图、动图的原图下载
- [x] 支持关注用户的作品下载和收藏插画的下载
- [x] 支持设置最低收藏限制数进行筛选下载/数据入库
- [x] 支持提供数据库开关，根据需要来决定是否使用数据库（默认True，False则不能使用API功能）

- [x] API：查询pid信息接口、随机插画接口，提供反代直连链接
- [ ] 日榜、周榜、月榜
- [ ] 通过API进行下载指定pid插画



**2、基本使用**

请参考<部署文档>完成环境搭建和依赖安装，接着运行

```
python scheduler.py
```



**3、关于PixiC与qq机器人**

目前使用Flask + go-cqhttp + PixiC可以实现随机涩图、查询指定pid信息等机器人功能。

效果如下，机器人还未开源出来，除了对接PixiC API还有其他功能，敬请期待吧。

+ 查询pid

![](https://i.loli.net/2021/01/02/PH2NnqUpZBCwo6c.png)

+ 随机插画

![](https://i.loli.net/2021/01/02/1XUNKrsnJRk6V95.png)



**写在结尾的话**

+ 之前存在一个V1.0版本，不过结构简单、功能也不多，后面准备关注画师作品下载和收藏下载功能单独做出来，后续会放到[Tools](https://github.com/WriteCode-ChangeWorld/Tools)上。
+ **现在的V2.0版本更健壮，功能更多。旨在简单配置后，敲下回车即能获取到Pixiv账号的数据和作品**