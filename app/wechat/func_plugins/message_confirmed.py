# !/usr/bin/env python
# _*_ coding:utf-8
# 确认消息已收到

from app import redis

def confirmed(openid):
    """　确认已收到id为'media_id'的信息推送
    """
    media_id = '';
    redis_prefix = "wechatmessage:confirmed:" + media_id
    redis.set(redis_prefix, openid_list, 7200)
    openid_list = redis.get(redis_prefix)
    if openid in openid_list:
        pass
        new_openid_list=openid_list.delete(openid)
    redis.set(redis_prefix, new_openid_list, 7200)
