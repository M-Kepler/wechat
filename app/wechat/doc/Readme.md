[TOC]

<!-- vim-markdown-toc GFM -->
* [任务报告](#任务报告)
    * [题目要求](#题目要求)
    * [任务书](#任务书)
    * [模块](#模块)
* [设计](#设计)
    * [搭建本地测试环境](#搭建本地测试环境)
    * [项目目录结构](#项目目录结构)
    * [微信和 wechatpy](#微信和-wechatpy)
        * [微信需知](#微信需知)
        * [未认证不可用接口](#未认证不可用接口)
        * [wechatpy需知](#wechatpy需知)
    * [数据库 redis 和 mysql](#数据库-redis-和-mysql)
        * [Redis 数据库](#redis-数据库)
        * [Redis 和 mysql](#redis-和-mysql)
    * [Flask](#flask)
        * [拾遗](#拾遗)
        * [请求,应答,会话](#请求应答会话)
        * [蓝图](#蓝图)
* [过程](#过程)
    * [UI 和文章排版](#ui-和文章排版)
* [清单](#清单)
    * [TODO](#todo)
    * [FIXME](#fixme)
    * [XXX](#xxx)
    * [DONE](#done)

<!-- vim-markdown-toc -->

# 任务报告


## 题目要求

通过班干部和同学之间的关系绑定，辅导员和学生之间的账号绑定，实现基于微信平台的消息推送，能够统计各类消息的已读状态。  
1、学生信息管理。  
2、辅导员信息管理。  
3、用户注册绑定。  
4、消息推送模块。包括批量筛选、公开信息和一对一信息，可回复，可评论。  
5、消息统计报表。  
6、班干部管理。  
7、会议签到管理。  
8、签到统计。  
要求：有微信开发和html5开发经验优先考虑。如有疑问，请电话联系。


## 任务书

1. 学生关注公众号后可以输入个人必要信息并绑定公众号
* 老师允许对学生对学生的信息进行管理
* 老师可以对某几个班级的学生、某些学生或一对一地进行消息的推送
* 消息推送模块。包括批量筛选、公开信息和一对一信息，可回复，可评论。
* 消息回复、附件下载、消息搜索、分类统计
* 会议签到，对签到情况汇报
* 可对消息进行分类查询，比如热度排行、关键字检索、
* 消息有轻重缓急分类，可以设置关注特定分类下的消息，
* 对消息送达情况进行统计汇总反馈
* 获取学生所处的位置（获取用户地理位置接口）
* 可以对学生进行分组，比如常用的班干部，学生会，某某协会等
* 学生可对消息进行评论、可针对特定消息进行提问咨询，进行对话询问留言
* 可以搜索获取老师的联系方式、事项办理流程、常用表格文档下载、
* 群发消息给用户，并且可以根据用户分组来群发，查看群发消息的成功数和失败数。
* 用户主动发消息给公众账号后，可以通过客户系统人工给用户发信息，类型包括文本、图片、语音、视频、音乐以及图文消息；
* 消息内容与对象可自定义的消息群发助手
* 可在公众号内进行签到
* 老师关注公众号后也进行消息的推送和管理
* 弄个机器人来处理简单消息

> * 话题讨论，增加活跃度（同学加上#可以在公众号内进行话题讨论）
> * 每日播报，可以为学生增加推送歌曲、文章、天气等，增加用户黏度


## 模块

* 登录绑定模块:
 * 包括登录口令和绑定验证

* 用户管理模块:
 * 包括用户角色
 * 用户的增删查改
 * 标记分组等

* 通知管理模块:
 * 通知编辑：可对通知分类、携带附件、发起投票等多样式的编辑
 * 通知推送：可批量筛选、公开和一对一、一对多推送，可进行回复评论
 * 对推送情况进行汇总报告

* 后台功能模块:
 * 用户可以进行关键字检索
 * 后台可提供常用文档下载
 * 用户可以进行签到
 * 可以在后台留言进行相关活动、讲座报名、活动签到
 * 老师可以使用微信进行简单的通知推送和管理功能


# 设计


## 搭建本地测试环境

* 由于要和微信的服务器进行对接,所以你的web必须要部署后才能提交url给微信,
但是如果每次都这样那实在是太累了.所以最好可以想写其他webapp那样,可以通过
localhost来看看效果,觉得不错后再部署起来.

* ```ngork```帮我们进行nat穿透, 把我们的ip映射到公网上,并分配一个可访问的二级子
域名, 这样就可以用这个域名来进行微信开发的调试了,
[用起来也很简单..](http://www.tuicool.com/articles/Zj2Mrqq)[用Ngrok搭建本地微信测试环境](http://www.2cto.com/weixin/201606/517386.html)

* 这时候把web运行起来,然后把映射得到的url放到公众号平台, 尝试接入成功就可以了.


## 项目目录结构

* 利用 ```flask``` 的蓝图特性，可以相对独立于其他蓝图得来实现```wechat``` 的功能,
    而其他蓝图实现管理的功能.

* 除了要与微信服务器打交道的其他功能写入到一个包``` plugins/``` 里面，
    就像插件一样, 也方便扩展功能.

* 处理微信消息响应以及相关的方法都写到```response.py```里

* 所有访问的路由都写在 ```view.py``` 里面, 把需要的方法从plugins导入就可以了,
    避免在一个路由下写太多的代码来实现一个功能.

* 数据库相关操作都放到```modeles/```下, 其中包括数据的更新/获取

* 至于配置文件还是使用```app/config.py```,里面配置了一个专门用于微信这边的配置类

* 其中,用装饰器来对应各种不同类型消息的回复;根据字典的key值调用对应的方法,都值得思考


## 微信和 wechatpy

### 微信需知

* 主动 / 被动调用接口
 * 被动模式: 用户主动发信息,才会出发微信回调公众号后台,并作出相应回答.
 * 主动调用接口: 后台主动发消息给某个用户(**难点**)

* [被动回复消息与客服消息](https://my.oschina.net/u/2472104/blog/684229)

* 暂时申请接口测试号进行开发  
测试帐号拥有微信公众平台所有的接口

* (高级群发接口](http://www.cnblogs.com/txw1958/p/weixin-mp-mass-send.html#.E5.88.A0.E9.99.A4.E7.BE.A4.E5.8F.91)
公众平台为订阅号提供了每天一条的群发权限 [ 需要认证 ]
高级群发接口的每日调用限制为10次(包括上传素材和群发消息的调用)
用户每月只能接收4条群发信息

* ```ACCESS_TOKEN```  
[详见微信开发文档](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/wiki/14/9f9c82c1af308e3b14ba9b973f99a8ba.html)<br />
`access_token`是公众号的全局唯一票据，(获取access_token需要appid和appsecret)公众号调用各接口时都需使用access_token。
access_token的存储至少要保留512个字符空间。access_token的有效期目前为2个小时，需定时刷新，
重复获取将导致上次获取的access_token失效。

* ```OPENID```  
当前公众号下某用户的唯一标识

* ```APPID & APPSECRET```  
服务号才有,appid=appkey是id编号,appsecret是签名密钥. 所以就是用来确定身份的

* ```JS-SDK```  
微信`JS-SDK`是微信公众平台面向网页开发者提供的基于微信内的网页开发工具包。通过使用微信JS-SDK，网页开发者可借助微信高效地使用拍照、
选图、语音、位置等手机系统的能力，同时可以直接使用微信分享、扫一扫、卡券、支付等微信特有的能力，为微信用户提供更优质的网页体验。
此文档面向网页开发者介绍微信JS-SDK如何使用及相关注意事项。

* ```JSAPI_TICKET```  
[参考文档JS-SDK使用权限签名算法](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/wiki/11/74ad127cc054f6b80759c40f77ec03db.html)<br />
jsapi_ticket是公众号用于调用微信JS接口的临时票据。正常情况下，jsapi_ticket
的有效期为7200秒，通过access_token来获取。由于获取jsapi_ticket的api调用次数
非常有限，频繁刷新jsapi_ticket会导致api调用受限，影响自身业务，开发者必须在
自己的服务全局缓存jsapi_ticket 。

* [获取网页授权](http://www.cnblogs.com/txw1958/p/weixin71-oauth20.html)```OAuth2.0```  
[理解OAuth2.0](http://www.ruanyifeng.com/blog/2014/05/oauth_2_0.html)<br/>
允许用户将第三方应用以安全且标准的方式获取该用户在某一个网站上存储的秘密资源, 而无需将用户名和密码提供给第
三方应用, ```OAuth```提供一个令牌,授权一个特定的网站在特定时间内访问特定资源.
> 1. 用户统一授权,获取code(code只能用一次,5分钟内没用就自动过期)
> 2. 通过code换取网页授权access_token
> 3. 刷新access_token(如果有需要)
> 4. 拉取用户信息(需scope为snsapi_userinfo)


* 微信```JsSDK```  
[如何使用JSSDK](http://www.jianshu.com/p/bb88f7520b9e)<br />
微信提供的面向网页开发者的基于微信内的网页开发工具包.

* `MEDIA_ID`  
公众号在回复图片, 语音, 视频的时候, 将使用`media_id`来调用相关文件
 * 临时素材: 每个素材`media_id`会在开发者上传或粉丝发送到微信服务器3天后自动删除
 * 永久素材:

* 群发消息  
首先讲图文消息用到的图片上传, 得到图片的url; 可以对某个分组的用户发消息; 可以查询群发状态


### 未认证不可用接口

* 未认证订阅号只可使用编辑模式下的自定义菜单功能，认证成功后才能使用自定义菜单的相关接口能力
* 个人未认证服务号是无法上传素材的FUCK!!!

* [多客服系统]需认证
* 针对特定openid用户发送信息都不行


### wechatpy需知

* replies.py

* client/

* oauth/


## 数据库 redis 和 mysql

### Redis 数据库  
[redis快速入门](http://www.yiibai.com/redis/redis_quick_guide.html)

### Redis 和 mysql

* redis怎么和mysql进行数据交互?  
不需要. 或者说只要在拿数据的时候检查一下```redis```中有没有数据, 没有就从数
据库中取然后更新到```redis```缓存就行了.  
所以这些获取和更新```表数据```的操作可以都写在```models/__init__.py```里.

* redis设计
选用```键值对```的Hashes类型结构
 * 需要和数据库对应的数据: ```wechat:user:openid : 值```
 * 其他不需要存数据库的进行合理设计:```wechat:user:auth:score:openid : 值```
 * 可使用冒号进行细分,是key更具可读性


## Flask


### 拾遗

* Markup  
`Flask`中自动转义功能默认是开启的，所以如果 name 包含 HTML ，它将会被自动转义。如果你
能信任一个变量，并且你知道它是安全的（例如一个模块把 Wiki 标记转换为 HTML）
你可以用** Markup 类或 |safe 过滤器在模板中把它标记为安全的**。

* Logger
```
app.logger.debug('A value for debugging')
app.logger.warning('A warning occurred(%d apples)', 42)
app.logger.error('An error occurred')
```

* Jsonify  
`Flask`中处理`json`时,对`json`加了一层封装,从而返回一个`Response`对象,
实现将自定义类型如`dict`转化成`json`格式. 在`view.py`看到返回了jsonify但在html
没看到处理过程,其实都卸载了`auth.js`里了,`js`里通过`$('#json_key')`, 就可以取`json`对应的值


### 请求,应答,会话

>[Flask框架—请求、应答与会话:Request/Response/Session](http://www.jianshu.com/p/0ced03604e24)  
`Flask`框架把`HTTP`请求被封装为`Request`对象,`HTTP`应答被封装成`Response`对象

* ```request```  
WSGI 服务器转发的http请求数据，Flask框架会将其封装为一个Request类的实例。
Request实例对象中包含了**关于一次HTTP请求的一切信息**, 常用的属性包括：
 * form - 记录请求中的表单数据。类型：MultiDict
 * args - 记录请求中的查询参数。类型：MultiDict
 * cookies - 记录请求中的cookie。类型：Dict
 * headers - 记录请求中的报文头。类型：EnvironHeaders
 * method - 记录请求使用的HTTP方法：GET/POST/PUT....。类型：string
 * environ - 记录WSGI服务器转发的环境变量。类型：Dict
 * url - 记录请求的URL地址。类型：string
 * 包含与客户端发送给服务器的数据的交互信息

* ```response```

* ```session```

* ```jsonify```

### 蓝图


# 过程

> 有些接口需要认证公众号才有权限

1. [用户绑定](http://blog.csdn.net/gf771115/article/details/46444333)
 * 用户回复后台指令 ---> response.py 响应后台指令 点击带链接的回复, 跳转到登录绑定界面,调用score.py处理
 * score.py下的login函数,用session模拟登录教务系统后会返回302跳转,表示登录成功;
 登录失败返回200

2. 用户关注公众号后会触发'subscribe'订阅事件, 这时候调用set_user_info将用户
信息保存到数据库

3. 绑定过程
用户后台发送指令或点击菜单触发`click`事件,然后就会收到一条绑定链接,点击链接进入`view.py/auth-score/<openid>`
然后`func_plugins/score.py`拿到用户输入的`studentid`和`studentpwd`进行模拟登录,并获取登录后的页面,
对页面内容进行解析,获取到需要的信息,保存数据库

4. 用户分组管理


## UI 和文章排版

* 方倍工作室有个图文编辑器,写好后直接复制过去应该行了



# 清单


## TODO

1. [未完成]
* [用户对消息的接受设置] 初步方案:User表增加个字段'subscribe_tag'保存用户选择的分类,比如'就业信息'
  发消息的时候先去看看用户的这个字段,如有'就业信息',才把这个openid加入到发送的用户列表[见wechatpy/message/send_mass_text]
  * 更进意见: 用户进行设置后,把用户加到那个分组下就可以了
* d


## FIXME

1. 明明绑定成功了,但却还是显示失败而且没有失败信息(/func_plugins/score.py)下的 ```redis_auth_prefix = "wechat:user:auth:score:"```
* 但是还没做根据设置分组这点, 而且之前设置了如果这个分组下的用户没有人的话,就会删掉这个分组


## XXX

1. 有待商榷的写法
* `response`下的按照dict来选择对应的处理函数


## DONE

1. 搬运下来的
* 确认情况放到数据库,显示在消息详情页上
* 多客服那里需要获取和更新access_token,jsapi_ticket, 现在无法验证正确性, 或许可以进shell调试一下
* 用户对消息的确认
* score.py还没完善, 登录教务系统爬取成绩, 应该不难吧
* auth.html里引用了很多js, 有一个是和后台view传数据的
* 一定要注意, 从redis获取出来values后一定要decode()一下, 因为直接从redis获取到的是b'content',要decode一下才能变成你想要的str
* access_token的管理(获取和缓存和更新), 我好像是用了wechatpy自带的缓存管理<有待商榷>
* 发布图文消息需要传入的参数是(标题, 文章描述,缩略图,url)那么当用户单击这个图文消息后是弹出网页吗?还是
怎么回事?我看别人发的图文消息, 点击后的链接都是微信那边的, 有些是一个自己域名下的url, 所以这个怎么回事
 * 永久素材上传到了微信的服务器,所以最后显示的是微信那边的url
* 回复音乐消息显示错误: Error code: 40007, message: invalid media_id hint: [NtZ4DA0886ge25]
 * 自己按照官网的说明写了个发送音乐消息的函数,调用成功
* 有时候打开自己开发的网页页面时很慢比如绑定页面, 其原因估计是因为ngrok
* OAuth,[code失效的问题,就是这个原因](http://tieba.baidu.com/p/5032467480)
 * ["errcode":40163](http://www.imooc.com/qadetail/207788)
 * [用session保存必要信息,避免多次请求code](https://segmentfault.com/q/1010000008778286/a-1020000008779944)
* 一个恶心我很久的问题**我添加永久图文素材时,总提示我media-id错误**,我还以为是我上传图片的问题(有两个接口,其中封面图片必须是永久图片素材(client.material.add),
另一个是临时素材(client.media.upload),图文消息内的图片就是用这个接口上传然后得到url,当到图文中....添加完就得到这个articles的media_id,就可以发送了
```
  File "/home/kepler/venv/lib/python3.5/site-packages/wechatpy/client/api/material.py", line 21, in add_articles
      'thumb_media_id': article['thumb_media_id'],
      TypeError: string indices must be integers
* 原因是,我只有一个图文消息然后构建的格式是:articles = {...},而正确的应该是articles = [{...}], 看了源码才知道...
* 添加图文素材接口:client.material.add_articles
```
* 用户可以自己设置愿意接受哪些通知了
用户点击setting链接后,选择自己愿意接受的通知(checkbox)然后后端通过getlist获取到用户已选项,保存这个list到数据库(保存方法和保存用户id的list到to_confirmed一样)
当用户再次点击设置时,用户曾经的设置会回显出来,做法是从数据库找出user_setting字段(是一个list)把它转str,然后传递给js,js根据str把对应id的checkbox勾选上



> tips
f = open('/home/kepler/Pictures/1.jpeg','rb')
<!-- 上传图文消息中需要用到的图片, 得到pic_url -->
client.media.upload_mass_image(f)

<!-- 上传到素材库,区别在于上面这个就是上面那个不占素材哭条数 -->
client.material.add('image',f)

