# !/usr/bin/env python
# _*_ coding:utf-8
# 确认消息已收到

import time, json
from flask import current_app
from app import redis
from app.wechat.models.pushpost import Pushtext,Pushnews
from app.wechat.models.user import WechatUser
from wechatpy import create_reply
from app.wechat.func_plugins.state import get_user_last_interact_time


def confirmed(openid):
    """　确认已收到id为'media_id'的信息推送 """
    user = WechatUser.query.filter_by(openid=openid).first()
    user_id = user.id

    last_push_time = redis.get("wechat:last_push_time")
    #  last_push_time = redis.get("wechat:last_pushtext_time")

    #  timeout = int(last_push_time.decode()) - int(get_user_last_interact_time(openid))
    #  current_app.logger.warning('超时%s' % timeout)


    last_push_cache = redis.hgetall("wechat:last_push")
    media_id = last_push_cache[b'media_id'].decode()
    pushtype = last_push_cache[b'pushtype'].decode()

    if pushtype == 'text':
        pushtext = Pushtext.query.filter_by(media_id=media_id).first()
        to_confirmed_before = pushtext.to_confirmed
        content = pushtext.content
        #  这里我是把list转为json存到数据库,所以去出来的时候要转回来
        to_confirmed = json.loads(to_confirmed_before)
        try:
            if user_id in to_confirmed:
                to_confirmed.remove(user_id)
                pushtext.to_confirmed = json.dumps(to_confirmed)
                pushtext.update()
                content = "你已确认获悉此条及在其之前发布的通知：\n【%s】"% content
                return content
            else:
                content = "【你已回复'收到', 无需重复回复!】"
                return content

        except Exception as e:
            current_app.logger.warning('用户重复回复了收到,错误信息:%s') % e
            return '出错, 请稍后在试试'

    elif pushtype == 'news':
        pushnews=Pushnews.query.filter_by(media_id=media_id).first()
        to_confirmed_before = pushnews.to_confirmed
        title=pushnews.title
        to_confirmed = json.loads(to_confirmed_before)
        current_app.logger.warning('to_confirmed_应该是个list %s' % to_confirmed)
        try:
            if user_id in to_confirmed:
                to_confirmed.remove(user_id)
                pushnews.to_confirmed = json.dumps(to_confirmed)
                pushnews.update()
                content = "你已确认获悉此条及在其之前发布的通知：\n【%s】" % title
                return content
            else:
                content = "【你已回复'收到', 无需重复回复!】"
                return content
        except Exception as e:
            current_app.logger.warning('用户重复回复了收到,错误信息:%s') % e
            cntent="出错, 请稍后在试试"
            return content

