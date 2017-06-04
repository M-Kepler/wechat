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


def sign(openid, location_x, location_y):
    metting_time = '会议时间'
    timeout = int(metting_time) - int(get_user_last_interact_time(openid))
    #  超时10分钟
    if timeout > 10 * 60:
        content = "【可能已过了签到时间：\n】"
        return content
    else:
        # TODO 这部分和消息确认差不多，需要先判断会议的时间地点再处理
        content = "你已完成会议签到, 签到时间：%s, 地点：%s, %s\n】" % (get_user_last_interact_time(openid), location_x, location_y)
        return content

