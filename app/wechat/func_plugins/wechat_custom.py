# !/usr/bin/env python
# _*_ coding:utf-8
import requests
import json
from flask import current_app
from ..utils import get_wechat_access_token, update_wechat_token


def send_text(openid, content):
    """ 组装文本回复数据 """
    data = {
            "touser":openid,
            "msgtype":"text",
            "text":
            {
                "content":content
                }
            }
    return send_message(data)


def send_music(openid, title, desc, music_url, thumb_media_id):
    """组装音乐回复数据 """
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
    """ 组装图文消息
    """
    data = {
        "touser":openid,
        "msgtype":"news",
        "news": {
            "content":content
        }
    }
    return send_message(data)


def send_message(data):
    """ 使用客服接口主动推送消息 """
    url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?" + \
            "access_token = %s" % get_wechat_access_token()
    try:
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=payload)
        response = r.json()
    except Exception as e:
        content = "客服接口超时或解析失败, 错误信息:%s\n提交内容:%s"
        current_app.logger.warning(content % (e, data))
    else:
        if response["errmsg"] != 'ok':
            content = "客服推送失败: %s\n推送内容:%s"
            current_app.logger.warning(content % (response, data))
            if response["errcode"] == 40001:
                #  access_token失效, 更新后重新发送
                update_wechat_token()
                send_message(data)
        return None


