### table : pixiv/bookmark


| 字段名        | 描述             | 备注                                                   |
| ------------- | ---------------- | ------------------------------------------------------ |
| id            |                  | 数据库自增                                             |
| uid           | 作者id           |                                                        |
| userName      | 作者             |                                                        |
| pid           | 作品id           | {pid}                                                  |
| purl          | 作品页面         | https://www.pixiv.net/artworks/{pid}                   |
| title         | 作品标题         |                                                        |
| tag           | 标签组           | 魅惑の谷間/魅惑的乳沟、下乳/南半「球」、青雲映す碧波、 |
| pageCount     | 作品页数         |                                                        |
| illustType    | 作品类型         | pageCount判断单图/多图，illustType为2为动图            |
| is_r18        | 是否属于r18      | 0:R18,1:正常(用tag中是否含R18判断)                     |
| viewCount     | 浏览人数         |                                                        |
| bookmarkCount | 收藏人数         |                                                        |
| likeCount     | 赞/喜欢人数      |                                                        |
| commentCount  | 评论数           |                                                        |
| urls          | 图片链接组       |                                                        |
| original      | original         |                                                        |
| path          | 图片本地存储目录 | folder类返回                                           |



### table : pxusers

| 字段名    | 描述                 | 备注       |
| --------- | -------------------- | ---------- |
| id        |                      | 数据库自增 |
| uid       | 作者id               |            |
| userName  | 作者                 |            |
| latest_id | 最新作品pid          | {pid}      |
| path      | 作者插画本地存储目录 |            |

