# !/usr/bin/env python
# _*_ coding:utf-8
# 确认消息已收到

import time, json
from flask import current_app
from app import redis
from app.wechat.models.pushpost import Pushtext
from app.wechat.models.user import WechatUser
from wechatpy import create_reply
from app.wechat.func_plugins.state import get_user_last_interact_time


def confirmed(openid):
    """　确认已收到id为'media_id'的信息推送 """
    user = WechatUser.query.filter_by(openid=openid).first()
    user_id = user.id

    last_push_time = redis.get("wechat:last_pushtext_time")
    #  timeout = int(last_push_time.decode()) - int(get_user_last_interact_time(openid))
    #  current_app.logger.warning('超时%s' % timeout)


    last_push_cache = redis.hgetall("wechat:last_pushtext")
    media_id = last_push_cache[b'media_id'].decode()

    pushtext = Pushtext.query.filter_by(media_id=media_id).first()

    to_confirmed_before = pushtext.to_confirmed
    content = pushtext.content

    to_confirmed = json.loads(to_confirmed_before)
    current_app.logger.warning('to_confirmed_应该是个list %s' % to_confirmed)
    try:
        to_confirmed.remove(user_id)
        pushtext.to_confirmed = json.dumps(to_confirmed)
        pushtext.update()
        content = "你已确认获悉此条及在其之前发布的通知：\n【%s】"% content
        return content
    except Exception as e:
        print(e)
        return False


