[TOC]

> Gratuation Project

## Tips

* 工程目录名称为````wechat````, 部署需要的配置文件都放在了````doc/tx_cloud/````下
* 还没说这些文件放在哪里,,怎么重启..这些都参照我的keplerblog

## 虚拟环境

````
virtualenv -p /usr/bin/python3.5 --no-site-packages venv
pip install Flask
pip install wechat-sdk
````

## 搭建本地测试环境

* 由于要和微信的服务器进行对接,所以你的web必须要部署后才能提交url给微信,
但是如果每次都这样那实在是太累了.所以最好可以想写其他webapp那样,可以通过
localhost来看看效果,觉得不错后再部署起来.

* ngork帮我们进行nat穿透, 把我们的ip映射到公网上,并分配一个可访问的二级子
域名, 这样就可以用这个域名来进行微信开发的调试了,
[用起来也很简单..](http://www.tuicool.com/articles/Zj2Mrqq)[用Ngrok搭建本地微信测试环境](http://www.2cto.com/weixin/201606/517386.html)


* 这时候把web运行起来,然后把映射得到的url放到公众号平台, 尝试接入成功就可以了.
