# coding:utf-8

from . import wechat
from flask import request, redirect, abort, current_app
from functools import wraps
from wechatpy import parse_message, create_reply
from wechatpy.replies import ImageReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException


#  微信接入认证装饰器
def check_wechat_signature(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        token='kepler'
        try:
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException:
            abort(403)
        return func(*args, **kwargs)
    return decorated_func


def get_wechat_access_token():
    """
    获取微信access_token, 公众号调用各接口时都需要使用access_token
    """
    access_token = redis.get("wechat.access_token")
    if access_token:
        return access_token
    else:
        current_app.logger.warning("从缓存获取 access_token 失败")
        return None

