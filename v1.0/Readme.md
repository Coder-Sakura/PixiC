> 下载关注画师的所有作品，





### 0215

+ 自动登录
+ 下载关注画师的所有作品，包括单图、多图、漫画和动图（合成）
+ 加入代理功能
+ 代理 ip 存储并进行活性校验



### 0331

+ 更新了文件夹比对机制
+ 代理影响抓取效率，暂时停止使用
+ 启动时会打印ip的抓取和校验，但实际功能已注释，有需要可以自己更改



### **2019.9-10**

+ selenium 自动获取本地 Cookie
+ 在使用爬虫前，需在Chrome上成功登陆自己的 Pixiv 账号
+ Chrome UserData目录配置清参考代码中去寻找（大概90-100行处）
+ 加入多图 PNG&JPG格式比对
+ 多图匹配机制更新，使用正则比对
+ 动图采用间隔形式合成，不建议采用帧率
+ 某些动图出现奇怪现象，可能是画师对动图中每张图的间隔设置不一，目前尚未解决



### 可能会帮助到你的地方

​	运行发现如下报错

```
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='proxy.seofangfa.com', port=443): Read timed out. (read timeout=5)
```

原因：代理网站获取失败,再启动一次就好



> 详细可参考：[我的Bog Coder-Sakura](https://coder-sakura.github.io/blog/)
>
> 使用Algolia搜索，输入pixiv检索即可