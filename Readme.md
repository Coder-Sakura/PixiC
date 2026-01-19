<div align="center">

# PixiC v2.1.12

## **[Pixiv](https://www.pixiv.net/) 收藏插画 & 关注画师数据采集工具**
**实现作品批量下载、元数据持久化、随机插画 API 及参数配置管理**

</div>

</br>

## 1. 支持功能
### 核心功能
- [x] **指定 UID 收藏下载**：支持指定用户的公开/未公开收藏作品的下载与数据收集
- [x] **指定 UID 关注下载**：支持指定用户的关注画师作品的批量下载
- [x] **支持单图、多图、动图的原图下载**
- [x] **反反爬机制**
  - [x] 模块周期执行
  - [x] 支持慢速模式保障下载，减少429错误导致的限制访问
  - [x] 支持单轮模块抓取上限
- [x] **Cookie管理**
  - [x] 支持获取 Chrome 浏览器登录的 Pixiv 账户并生成 cookie 文件持久化
  - [x] 支持通过用户自定义 cookie 池（单个或多个 cookie）

</br>

### 其他功能
- [x] API 支持：提供查询 PID 信息、随机插画接口（含反代链接）
- [x] 日志记录功能

> PixiC提供了丰富的自定义配置，可以通过 config.py 修改，后续会开发GUI界面进行可视化操作
- [x] 配置参数
  - [x] 采集功能 --> 支持增量更新开关、各模块开关等
  - [x] 支持最低收藏数过滤 --> [相关配置](https://github.com/Coder-Sakura/PixiC/wiki/%E5%85%B3%E4%BA%8EPixiC%E9%85%8D%E7%BD%AE%E7%9A%84%E4%B8%89%E8%A8%80%E4%B8%A4%E8%AF%AD#%E5%87%A0%E7%A7%8D%E5%B8%B8%E8%A7%81%E5%9C%BA%E6%99%AF%E7%9A%84config%E6%96%87%E4%BB%B6%E9%85%8D%E7%BD%AE) 
  - [x] 支持周期轮询设置
  - [x] 支持数据库采集数据、数据库启用开关
  - [x] 支持插画下载路径配置

</br>

## 2. 基本使用
请参考部署文档完成环境搭建和依赖安装
+ 部署文档：  [WIKI](https://github.com/Coder-Sakura/PixiC/wiki) (推荐) 或 [Blog](http://mybot.top/blog/2020/06/24/pixic-bu-shu/)
+ 运行截图戳这：[运行截图](https://github.com/Coder-Sakura/PixiC/wiki/运行截图)
+ 注意事项戳这：[注意事项](https://github.com/Coder-Sakura/PixiC/wiki/%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9)

</br>

核心步骤如下：

```bash
# 1. 克隆仓库
git clone https://github.com/Coder-Sakura/PixiC.git

# 2. 安装依赖
cd PixiC/v2.0
pip install -r requirements.txt

# 3. 运行调度程序
python scheduler.py
```

</br>

## 3. 用途展示
### 3.1 随机pixiv插画

> PixiC API + [Mybot机器人](https://github.com/WriteCode-ChangeWorld/mybot)或其他qq机器人 可实现功能

+ 查询pid (预览图片已去除)
+ 随机插画 (预览图片已去除)



### 3.2 阅读3.0 订阅源
> 可自行部署

订阅源链接: [蓝奏云](https://python.lanzout.com/b0bsanjmj)  密码: hsvs (已失效)

</br>

## 待填的坑 todo
- [ ] GUI界面及优化
- [ ] 日榜、周榜、月榜作品采集
- [ ] 任务通知：异常状态通知用户

</br>

## 结尾的话

---

+ 希望可以提交`issue`和`pr`来帮助本项目进行完善，也欢迎`fork`和`star`本项目以对作者表示支持，感谢！
+ 本仓库仅用于学习与交流使用，因使用而产生的一切纠纷与原作者无关。
