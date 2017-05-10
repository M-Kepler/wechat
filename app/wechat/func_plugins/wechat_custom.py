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


def send_music_self(openid, title, desc, music_url, thumb_media_id):
    """ 自己写的发音乐消息
    """
    data = {
        "touser": openid,
        "msgtype": "music",
        "music":
        {
            "title": title,
            "description": desc,
            "musicurl": music_url,
            "hqmusicurl": music_url,
            "thumb_media_id": thumb_media_id
        }
    }
    return send_message(data)



def send_news(openid, content):
    """ 发送图文消息 """
    wechat = init_wechat_sdk()
    client = wechat['client']
    return client.message.send_articles(openid, content)


def send_message(data):
    """ 使用客服接口主动推送消息 """
    access_token = get_wechat_access_token()
    access_token = access_token.decode()
    url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?" + "access_token=%s" % access_token
    try:
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=payload)
        response = r.json()
    except Exception as e:
        content = u"客服接口超时或解析失败，错误信息：%s\n提交内容：%s"
        current_app.logger.warning(content % (e, data))
    else:
        if response["errmsg"] != 'ok':
            content = u"客服推送失败: %s\n推送内容：%s"
            current_app.logger.warning(content % (response, data))
            if response["errcode"] == 40001:
                # access_token 失效，更新 # 再发送
                update_wechat_token()
                send_message(data)
        return None

