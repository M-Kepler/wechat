# !/usr/bin/env python
# _*_ coding:utf-8

import requests, json
from flask import current_app
import urllib.request
from . import wechat_custom


def get_douban_fm(openid):
    """ 随机豆瓣FM音乐 """
    url = 'https://douban.fm/j/v2/playlist?' + \
        'app_name=radio_website&version=100&channel=0&type=n'
    try:
        r = requests.get(url, timeout=5)
        result = r.json()["song"][0]
        desc = result["artist"] + u'-建议WiFi下播放'
        music_url = result["url"]
        title = result["title"]
    except Exception as e:
        current_app.logger.warning(u"豆瓣FM请求或解析失败: %s" % e)
        context = u"网络繁忙，请稍候重试"
        wechat_custom.send_text(openid, context)
    else:
        # 客服接口推送音乐必须要有 thumb_media_id
        thumb_media_id = current_app.config["MUSIC_THUMB_MEDIA_ID"]
        wechat_custom.send_music_self(openid,title, desc, music_url, thumb_media_id)


def get_netease_music(word):
    """ 搜索网易云音乐 """
    baseurl = r'http://s.music.163.com/search/get/?type=1&s='
    qword = urllib.request.quote(word)
    url = baseurl + qword + r'&limit=1&offset=0'
    resp = urllib.request.urlopen(url)
    music = json.loads(resp.read().decode())
    return music


def query_music(openid, music_title):
    word = music_title
    music = get_netease_music(word)
    title = music['result']['songs'][0]['name']
    desc = '♫ 来自网易云音乐♫'
    music_url = music['result']['songs'][0]['audio']
    thumb_media_id = current_app.config["MUSIC_THUMB_MEDIA_ID"]
    #  wechat_custom.send_music(openid, music_url, thumb_media_id, title, desc)
    wechat_custom.send_music_self(openid,title, desc, music_url, thumb_media_id)


