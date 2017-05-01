# !/usr/bin/env python
# _*_ coding:utf-8

from app import redis


def set_user_last_interact_time(openid, timestamp):
    """ 保存最后一次交互时间 """
    redis.hset('wechat:user:' + openid, 'last_interact_time', timestamp)
    return None


def get_user_last_interact_time(openid):
    """ 获取最后一次交互时间 """
    last_time = redis.hget('wechat:user:' + openid, 'last_interact_time')
    if last_time:
        return last_time
    else:
        return 0


