# !/usr/bin/env python
# _*_ coding:utf-8
# 一些需要定时检查的任务

from ..utils import update_wechat_token
def update_access_token():
    """
    定时更新微信的access_token
    """
    update_wechat_token()
