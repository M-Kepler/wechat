# coding:utf-8
#  TODO global client为什么会保存?

from . import wechat
from app import redis
from flask import request, redirect, abort, current_app, session
from functools import wraps
from wechatpy import parse_message, create_reply
from wechatpy.replies import ImageReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import WeChatClient
from Crypto import Random
from Crypto.Cipher import AES
import time, random, string, base64


wechat = {}

def init_wechat_sdk():
    """ 初始化微信sdk
    设置保存一些参数
    """
    wechat_client = WeChatClient(current_app.config['APPID'],current_app.config['APPSECRET'])

    access_token = redis.get("wechat:access_token")
    jsapi_ticket = redis.get("wechat:jsapi_ticket")
    token_expires_at = redis.get("wechat:access_token_expires_at")
    ticket_expires_at = redis.get("wechat:jsapi_ticket_expires_at")
    if access_token and jsapi_ticket:
        wechat = {
                'client':wechat_client,
                'appid' : current_app.config['APPID'],
                'appsecret' : current_app.config['APPSECRET'],
                'token' : current_app.config['TOKEN'],
                'access_token' : access_token,
                'access_token_expires_at':int(token_expires_at),
                'jsapi_ticket' : jsapi_ticket,
                'jsapi_ticket_expires_at':int(ticket_expires_at)
                }
        return wechat
    #  没有缓存
    else:
        access_token_dic = wechat_client.fetch_access_token()
        access_token = access_token_dic['access_token']
        token_expires_at = access_token_dic['expires_in']

        jsapi_ticket_dic = wechat_client.jsapi.get_ticket()
        jsapi_ticket = jsapi_ticket_dic['ticket']
        ticket_expires_at = jsapi_ticket_dic['expires_in']

        redis.set("wechat:access_token", access_token, 7000)
        redis.set("wechat:access_token_expires_at", token_expires_at, 7000)
        redis.set("wechat:jsapi_ticket", jsapi_ticket, 7000)
        redis.set("wechat:jsapi_ticket_expires_at", ticket_expires_at, 7000)

        wechat = {
                'client':wechat_client,
                'appid' : current_app.config['APPID'],
                'appsecret' : current_app.config['APPSECRET'],
                'token' : current_app.config['TOKEN'],
                'access_token' : access_token,
                'access_token_expires_at':int(token_expires_at),
                'jsapi_ticket' : jsapi_ticket,
                'jsapi_ticket_expires_at':int(ticket_expires_at)
                }
        return wechat



def check_wechat_signature(func):
    """ 微信签名认证装饰器 """
    @wraps(func)
    def decorated_func(*args, **kwargs):
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        #  token='kepler'
        token = current_app.config['TOKEN']
        try:
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException:
            abort(403)
        return func(*args, **kwargs)
    return decorated_func


def oauth_request(func):
    """ OAuth网页授权接入装饰器 """
    @wraps(func)
    def decorated_func(*args, **kwargs):
        code = request.args.get('code', None)
        wechat_client = WeChatClient(current_app.config['APPID'],current_app.config['APPSECRET'])
        url = wechat_client.oauth.authorize_url(request.url)
        if code:
            try:
                user_info = wechat_client.oauth.get_user_info(code)
            except Exception as e:
                print (e.errmsg, e.errcode)
                abort(403)
            else:
                session['user_info'] = user_info
        else:
            return redirect(url)
        return decorated_func(*args, **kwargs)
    return decorated_func


def update_wechat_token():
    """ 刷新access_token 和 jsapi_ticket
    """
    wechat = init_wechat_sdk()
    wechat_client = wechat['client']
    access_token_dic = wechat_client.fetch_access_token()
    access_token = access_token_dic['access_token']
    token_expires_at = access_token_dic['expires_in']

    redis.set("wechat:access_token", access_token, 7000)
    redis.set("wechat:access_token_expires_at", token_expires_at, 7000)

    jsapi_ticket_dic = wechat_client.jsapi.get_ticket()
    jsapi_ticket = jsapi_ticket_dic['ticket']
    ticket_expires_at = jsapi_ticket_dic['expires_in']

    redis.set("wechat:jsapi_ticket", jsapi_ticket, 7000)
    redis.set("wechat:jsapi_ticket_expires_at", ticket_expires_at, 7000)

    current_app.logger.warning("运行update_wechat_token结束")


def get_wechat_access_token():
    """ 从redis获取access_token """
    access_token = redis.get("wechat:access_token")
    if access_token:
        return access_token
    else:
        current_app.logger.warning("从缓存获取 access_token 失败")
        return None


def get_jsapi_signature_data(url):
    """ 获取jsapi前端签名数据 """
    timestamp = int(time.time())
    noncestr = generate_random_str(16)
    wechat = init_wechat_sdk()
    client = wechat['client']
    ticket = wechat['jsapi_ticket']
    wechat_client = WeChatClient(current_app.config['APPID'], current_app.config['APPSECRET'])
    signature = wechat_client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp, url)
    return{
        "appId" : current_app.config['APPID'],
        "timestamp" : timestamp,
        "nonceStr" : noncestr,
        "signature" : signature
    }


def generate_random_str(N):
    """ 生成随机字符串 """
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))


class AESCipher:
    """ 加密解密方法
    http://stackoverflow.com/questions/12524994
    """
    def __init__(self, key):
        self.BS = 16
        self.pad = lambda s: s + \
            (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        self.key = key

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]))


