# CREATE DATABASE moe;
CREATE DATABASE IF NOT EXISTS moe DEFAULT CHARSET utf8mb4;
USE moe;

# 2019-11-24 05:36:
CREATE TABLE pixiv(
  id int AUTO_INCREMENT PRIMARY KEY,
  uid int(10) NOT NULL,
  userName varchar(100) NOT NULL,
  pid int(10) NOT NULL,
  purl varchar(255) NOT NULL,
  title varchar(255) NOT NULL,
  tag varchar(999) NOT NULL,
  pageCount int(3) NOT NULL,
  illustType tinyint(3) NOT NULL,
  is_r18 tinyint(1) NOT NULL,
  is_ai tinyint(1) NOT NULL,
  score float(5,3) NOT NULL,
  illust_level varchar(20) NOT NULL,
  viewCount int NOT NULL,
  bookmarkCount int NOT NULL,
  likeCount int NOT NULL,
  commentCount int NOT NULL,
  urls varchar(999) NOT NULL,
  original varchar(255) NOT NULL,
  path varchar(255) NOT NULL
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

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
# 2019-11-24 05:36
CREATE TABLE bookmark(
  id int AUTO_INCREMENT PRIMARY KEY,
  uid int(10) NOT NULL,
  userName varchar(100) NOT NULL,
  pid int(10) NOT NULL,
  purl varchar(255) NOT NULL,
  title varchar(255) NOT NULL,
  tag varchar(999) NOT NULL,
  pageCount int(3) NOT NULL,
  illustType tinyint(3) NOT NULL,
  is_r18 tinyint(1) NOT NULL,
  is_ai tinyint(1) NOT NULL,
  score float(5,3) NOT NULL,
  illust_level varchar(20) NOT NULL,
  viewCount int NOT NULL,
  bookmarkCount int NOT NULL,
  likeCount int NOT NULL,
  commentCount int NOT NULL,
  urls varchar(999) NOT NULL,
  original varchar(255) NOT NULL,
  path varchar(255) NOT NULL
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;



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


# 随机获取多条数据
SELECT * FROM pixiv
WHERE id >= ((SELECT MAX(id) FROM bookmark)-(SELECT MIN(id) FROM bookmark)) * RAND() 
+ (SELECT MIN(id) FROM bookmark)
LIMIT 1;