# !/usr/bin/env python
# _*_ coding:utf-8
"""
教务系统绑定
成绩查询
"""
import requests
import time
from ..models import set_user_student_info, set_user_realname_and_classname


def login(studentid, studentpwd, url, session, proxy):
    """
    登录先获取 cookie
    :studentid: TODO
    :studentpwd: TODO
    :url: TODO
    :session: TODO
    :proxy: TODO
    :returns: TODO
    """
