# !/usr/bin/env python
# _*_ coding:utf-8

import requests
import ast
from . import wechat_custom
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import current_app
from app import redis


def get(openid):
    """获取最新的学院新闻"""
    # 优先读取缓存
    redis_key = 'wechat:school_news'
    news_cache = redis.get(redis_key)
    if news_cache:
        content = ast.literal_eval(news_cache.decode())
        wechat_custom.send_news(openid, content)
    else:
        url = current_app.config['SCHOOL_NEWS_URL']
        try:
            res = requests.get(url, timeout=6)
        except Exception as e:
            app.logger.warning(u'学院官网连接超时出错：%s' % e)
            content = u'学院官网连接超时\n请稍后重试'
            wechat_custom.send_text(openid, content)
        else:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.find("tr", {"class":"newsMoreLine"}).find_all('a')[:5]  # 图文推送5数
            content = []
            for row in rows:
                title = row.text
                link = urljoin(url, row['href'])
                data = {
                    "title": title,
                    "picurl":'http://d.hiphotos.baidu.com/baike/w%3D268%3Bg%3D0/sign=22959be8277f9e2f70351a0e270b8e19/35a85edf8db1cb13ca4a151ddd54564e92584b98.jpg',
                    "description":"",
                    "url": link
                }
                content.append(data)
            #  缓存结果12小时
            redis.set(redis_key, content, 3600 * 12)
            wechat_custom.send_news(openid, content)

