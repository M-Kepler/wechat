# !/usr/bin/env python
# _*_ coding:utf-8
import requests
import json
from flask import current_app
from ..utils import get_wechat_access_token, update_wechat_token, init_wechat_sdk


def send_text(openid, content):
    """ 文本回复数据 """
    wechat = init_wechat_sdk()
    client = wechat['client']
    return client.message.send_text(openid, content)


def send_image(openid, image_media_id):
    """ 发送图片消息 """
    wechat = init_wechat_sdk()
    client = wechat['client']
    return client.message.send_image(openid, image_media_id)


def send_voice(openid, voice_media_id):
    """ 语音回复信息 """
    wechat = init_wechat_sdk()
    client = wechat['client']
    return client.message.send_voice(openid, voice_media_id)


def send_music(openid, music_url, thumb_media_id, title, desc):
    """FIXME 组装音乐回复数据 """
    wechat = init_wechat_sdk()
    client = wechat['client']
    return client.message.send_music(openid, music_url, thumb_media_id, title, desc)


def send_news(openid, content):
    """ 发送图文消息 """
    wechat = init_wechat_sdk()
    client = wechat['client']
    return client.message.send_articles(openid, content)
