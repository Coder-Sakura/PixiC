部署文档： [Wiki](https://github.com/Coder-Sakura/PixiC/wiki),  [Blog](http://00102400.xyz/blog/2020/06/24/pixic-bu-shu/)

API文档：[API](https://github.com/Coder-Sakura/PixiC/wiki/API文档),  [Blog](http://00102400.xyz/blog/2020/07/08/pixicapi/)

[运行截图](https://github.com/Coder-Sakura/PixiC/wiki/运行截图)戳这里



1. PixiC目前功能及后续功能：

- [x] 1. 获取Chrome上登录的Pixiv账户信息

- [x] 2. 关注画师插画下载

- [x] 3. 用户收藏插画下载

- [x] 4. 添加DB_ENABLE开关以控制是否使用数据库

  （默认True使用；设置为False，则不能使用API功能）

- [x] 5. API—查询指定pid信息 (数据库)

- [x] 6. API—随机返回插画，最多10张，最多指定2个tag (数据库)

- [x] 7. 生成反代链接 (可直接访问)

- [x] 8. 收藏数筛选下载

- [x] 9. 单图、多图、动图

- [ ] 10. 日榜、周榜、月榜

- [ ] 11. 通过API进行下载指定pid插画 (Pixiv)

> 有API地址，理论上十分容易对接机器人。



+ V1.0 简单，有一段时间未维护，目前重心在2.0版本
+ **V2.0 更健壮，功能更多。旨在简单配置后，敲下回车即能获取到Pixiv账号的数据和作品**