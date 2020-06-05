use test;
create DATABASE test1127;
create table pra(
  id int AUTO_INCREMENT PRIMARY KEY,
  name varchar(10)
);
# 插入数据
INSERT INTO pra VALUES(null,'Ame');
# 查询数据
select * from pra;
# 修改自增id为num
truncate pra;
# alter table pra AUTO_INCREMENT 1; 
# 删除表
drop table pra;
# 删除表中的数据
DELETE FROM pra;

insert into pra values(5,'sakura1')

# 查看mysql存储引擎
show engines \G;

# show create table pra;

# 看自己的数据库是否是自动commit
# show variables like '%autocommit%';
SHOW FULL COLUMNS FROM stock_product;


# 2019-11-24 05:36:
CREATE TABLE pixiv(
  id int AUTO_INCREMENT PRIMARY KEY,
  uid int(10) NOT NULL,
  userName varchar(100) NOT NULL,
  pid int(10) NOT NULL,
  purl varchar(255) NOT NULL,
  title varchar(255) NOT NULL,
  tag varchar(300) NOT NULL,
  pageCount int(3) NOT NULL,
  illustType tinyint(3) NOT NULL,
  is_r18 tinyint(1) NOT NULL,
  viewCount int NOT NULL,
  bookmarkCount int NOT NULL,
  likeCount int NOT NULL,
  commentCount int NOT NULL,
  urls varchar(999) NOT NULL,
  original varchar(255) NOT NULL,
  path varchar(255) NOT NULL
# )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
# 存储emoji表情
# 1、
# 更改表的字符集为utf8mb4
# 能存储以4个字节为单位的emoji表情
# 表情是按照4个字节一个单位进行编码的
# 而utf-8编码在mysql数据库中默认是按照3个字节一个单位进行编码的.
# 2、
# 2.1修改mysql的配置文件mysql/bin/my.ini
# 在my.ini中添加内容
# [client]
# default-character-set=utf8mb4
# [mysql]
# default-character-set=utf8mb4
# [mysqld]
# character-set-client-handshake=FALSE
# character-set-server=utf8mb4
# collation-server=utf8mb4_unicode_ci
# init_connect='SET NAMES utf8mb4'
# 2.2重启数据库
# 2.3修改数据表的编码为utf8mb4
# ALTER TABLE TABLE_NAME CONVERT TO CHARACTER SET utf8mb4;
# ====
# 查看数据表的字符集
SHOW FULL COLUMNS FROM pixiv;


# 2020-04-15 21:30 
CREATE TABLE pxusers(
  id int AUTO_INCREMENT PRIMARY KEY,
  uid int(10) NOT NULL,
  userName varchar(100) NOT NULL,
  latest_id int(10) NOT NULL,
  path varchar(255) NOT NULL
  # total int(10) NOT NULL
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

# 2020-05-11 10:21
# 2019-11-24 05:36:
CREATE TABLE bookmark(
  id int AUTO_INCREMENT PRIMARY KEY,
  uid int(10) NOT NULL,
  userName varchar(100) NOT NULL,
  pid int(10) NOT NULL,
  purl varchar(255) NOT NULL,
  title varchar(255) NOT NULL,
  tag varchar(300) NOT NULL,
  pageCount int(3) NOT NULL,
  illustType tinyint(3) NOT NULL,
  is_r18 tinyint(1) NOT NULL,
  viewCount int NOT NULL,
  bookmarkCount int NOT NULL,
  likeCount int NOT NULL,
  commentCount int NOT NULL,
  urls varchar(999) NOT NULL,
  original varchar(255) NOT NULL,
  path varchar(255) NOT NULL
# )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;



# 2020-03-24 21:50 绅士天堂
CREATE TABLE shenshitiantang(
  id int AUTO_INCREMENT PRIMARY KEY,
  title varchar(255) NOT NULL,
  url varchar(255) NOT NULL
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
# ===================
SELECT COUNT(uid) FROM pxusers WHERE uid=976389;

# ===================
INSERT INTO pxusers(uid,userName,latest_id,path) 
VALUES(3872398,'孟達',80703306,'H:\\se19\\3872398--孟達');
# ===================
SELECT COUNT(uid) FROM pxusers WHERE uid=3872398;
# ===================
INSERT INTO pixiv(
uid,userName,pid,purl,title,tag,pageCount,illustType,is_r18,
viewCount,bookmarkCount,likeCount,commentCount,urls,original,path)
VALUES(
0, "None", 0, "None", "None",
"None", 
0, 0, 0, 0, 0, 0, 
0, 
'{"mini": "https://i.pximg.net/c/48x48/img-master/img/2020/02/27/19/20/26/79760358_p0_square1200.jpg", "thumb": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2020/02/27/19/20/26/79760358_p0_square1200.jpg", "small": "https://i.pximg.net/c/540x540_70/img-master/img/2020/02/27/19/20/26/79760358_p0_master1200.jpg", "regular": "https://i.pximg.net/img-master/img/2020/02/27/19/20/26/79760358_p0_master1200.jpg", "original": "https://i.pximg.net/img-original/img/2020/02/27/19/20/26/79760358_p0.jpg"}',
"None", 
"None");
# ==================
SELECT COUNT(*) FROM pixiv WHERE uid=5795415;
SELECT COUNT(*) FROM pixiv;

SELECT * FROM pixiv;
SELECT COUNT(*),path FROM pixiv WHERE pid=72527136;

SELECT * FROM pixiv WHERE 
#tag like "%パイズリ%";
bookmarkCount > 3000;

SELECT * FROM pixiv WHERE   pid=81265370;
SELECT * FROM pxusers WHERE uid=2348589;

# ==================
DELETE FROM pixiv WHERE uid=5795415;
# ====================
SELECT LENGTH(urls) FROM pixiv;
# ====================
SHOW FULL COLUMNS FROM pixiv;

SELECT viewCount,bookmarkCount,likeCount,commentCount,pid 
FROM pixiv WHERE pid=81265370;



# ===========================
SELECT * FROM bookmark
WHERE bookmarkCount>3000
AND tag LIKE "%%";

SELECT * FROM bookmark ORDER BY rand() LIMIT 1;

# 随机返回一条数据
# 参考https://blog.csdn.net/shenzhou_yh/article/details/90550090
# 随机获取一条数据时效率不错
SELECT pid,tag FROM bookmark AS t1 
SELECT * FROM bookmark AS t1
JOIN (SELECT ROUND(RAND() * ((SELECT MAX(id) FROM bookmark)-(SELECT MIN(id) FROM bookmark))
+(SELECT MIN(id) FROM bookmark)) AS id) AS t2 WHERE t1.id >= t2.id
AND tag LIKE "%巨乳%" AND tag LIKE "%萝莉%" AND bookmarkCount>3000
ORDER BY t1.id LIMIT 1;

SELECT * FROM bookmark AS t1
JOIN (SELECT ROUND(RAND() * MAX(id) AS id) AS t2 WHERE t1.id >= t2.id ORDER BY t1.id;
AND tag LIKE "%巨乳%" AND tag LIKE "%萝莉%" AND bookmarkCount>3000
ORDER BY t1.id LIMIT 1;

SELECT * FROM bookmark AS t1;

# 随机获取多条数据
SELECT * FROM pixiv
WHERE id >= ((SELECT MAX(id) FROM bookmark)-(SELECT MIN(id) FROM bookmark)) * RAND() 
+ (SELECT MIN(id) FROM bookmark)
LIMIT 1;


SELECT COUNT(*) FROM bookmark;
SELECT * FROM bookmark WHERE pid=81503466;
SELECT * FROM bookmark ORDER BY id DESC LIMIT 0,10;
SELECT * FROM bookmark WHERE id=(SELECT MAX(id) FROM bookmark);




SELECT COUNT(*),path FROM 'bookmark' WHERE pid='81503466';

