#!/usr/bin/env python
# _*_ coding:utf-8

"""
* 查询/更新各项数据, redis和mysql的交互

* redis缓存键值设计
  key       value
表名:列名    列值
redis_prefix = "wechat:user:"
redis_prefix + openid, 'nickname'

"""


import time
from app import db, redis
from flask import current_app
from .user import WechatUser
from .auth import Auth
from wechatpy.oauth import WeChatOAuth


def set_user_info(openid):
    """
    保存用户信息
    """
    redis_prefix = "wechat:user:"
    cache = redis.hexists(redis_prefix + openid, 'nickname')

    #  如果不存在缓存, 就从数据库中读取, 并更新缓存
    if not cache:
        user_info = WechatUser.query.filter_by(openid=openid).first()
        if not user_info:
            try:
                #  从框架中得到用户的信息, 并保存到数据库
                user_info = WechatUser.get_user_info(openid)
                if 'nickname' not in user_info:
                    raise KeyError(user_info)
            except Exception as e:
                app.logger.warning('获取用户信息出错, 错误信息:%s' % e)
                user_info = None
            else:
                user = WechatUser(
                        openid = user_info['openid'],
                        nickname = user_info['nickname'],
                        sex = user_info['sex'],
                        province = user_info['province'],
                        city = user_info['city'],
                        country = user_info['country'],
                        headimgurl = user_info['headimgurl']
                        )
                #  多设置一个save方法比用db.session.add(user)好, 感觉
                user.save()
                user_info = user

        if user_info:
            #  把用户信息从数据库写入缓存
            redis.hmset(redis_prefix + user_info.openid, {
                "nickname": user_info.nickname,
                "realname": user_info.realname,
                "classname": user_info.classname,
                "sex": user_info.sex,
                "province": user_info.province,
                "city": user_info.city,
                "country": user_info.country,
                "headimgurl": user_info.headimgurl,
                "regtime": user_info.regtime
                })

    else:
        timeout = int(time.time())-int(get_user_last_interact_time(openid))
        if timeout > 24 * 60 * 60:
            try:
                user_info = WeChatOAuth.get_user_info(openid)
                if 'nickname' not in user_info:
                    raise KeyError(user_info)
            except Exception as e:
                app.logger.warning('获取用户信息 API 出错: %s' % e)
            else:
                user = WechatUser.query.filter_by(openid=openid).first()
                user.nickname = user_info['nickname'],
                user.sex = user_info['sex'],
                user.province = user_info['province'],
                user.city = user_info['city'],
                user.country = user_info['country'],
                user.headimgurl = user_info['headimgurl'],
                user.update()

                redis.hmset(redis_prefix + user_info.openid, {
                    "nickname": user_info['nickname'],
                    "sex": user_info['sex'],
                    "province": user_info['province'],
                    "city": user_info['city'],
                    "country": user_info['country'],
                    "headimgurl": user_info['headimgurl']
                })
        return None


def is_user_exists(openid):
    """
    判断用户是否存在数据库中
    """
    redis_prefix = "wechatpy:user:"
    cache = redis.exists(redis_prefix + openid)
    if not cache:
        user_info = WechatUser.query.filter_by(openid=openid).first()
        if not user_info:
            return False
        else:
            return True
    else:
        return True



def set_user_student_info(openid, studentid, studentpwd):
    """
    写入绑定的教务管理系统帐号
    """
    redis_prefix = "wechat:user:"
    auth_info = Auth.query.filter_by(openid=openid).first()
    if not auth_info:
        auth = Auth(openid=openid,
                studentid = studentid,
                studentpwd = studentpwd
                )
        auth.save()
    else:
        auth_info.studentid = studentid
        auth_info.studentpwd = studentpwd
        auth_info.update()

    #  写入缓存
    redis.hmset(redis_prefix + openid, {
        "studentid" : studentid,
        "studentpwd" : studentpwd
    })


def get_user_info(openid):
    """
    获取绑定的教务系统帐号
    """
    redis_prefix = "wechat:user:"
    user_info_cache = redis.hgetall(redis_prefix + openid)

    if 'studentid' in user_info_cache and 'studentpwd' in user_info_cache:
        return user_info_cache
    else:
        auth_info = Auth.query.filter_by(openid=openid).first()
        if auth_info and auth_info.studentid and auth_info.studentpwd:
            #  写入缓存
            redis.hmset(redis_prefix + openid, {
                "studentid" : auth_info.studentid,
                "studentpwd" : auth_info.studentpwd,
                })
            user_info_cache['studentid'] = auth_info.studentid
            user_info_cache['studentpwd'] = auth_info.studentpwd
            return user_info_cache
        else:
            return False


def get_all_auth_info():
    """
    读取所有授权的帐号信息
    """
    auth_info = Auth.query.all()
    return auth_info


def set_user_library_info(openid, libraryid, librarypwd):
    """
    写入绑定的图书馆帐号
    """
    redis_prefix = "wechat:user:"
    auth_info = Auth.query.filter_by(openid=openid).first()
    if not auth_info:
        auth = Auth(
                openid = openid,
                studentid = studentid,
                studentpwd = studentpwd
                )
        auth.save()
    else:
        auth_info.libraryid = libraryid
        auth_info.librarypwd = librarypwd
        auth_info.update()

    #  写入缓存
    redis.hmset(redis_prefix + openid, {
        "libraryid":libraryid,
        "librarypwd":librarypwd
        })


def get_user_library_info(openid):
    """
    获取绑定的图书馆帐号
    """
    redis_prefix = "wechat:user:"
    user_info_cache = redis.hgetall(redis_prefix + openid)
    if 'libraryid' in user_info_cache and 'librarypwd' in user_info_cache:
        return user_info_cache
    else:
        auth_info = Auth.query.filter_by(openid=openid).first()
        if auth_info and auth_info.libraryid and auth_info.librarypwd:
            #  写入缓存
            redis.hmset(redis_prefix + openid, {
                "libraryid" : auth_info.libraryid,
                "librarypwd" : auth_info.librarypwd,
                })
            user_info_cache['libraryid'] = auth_info.libraryid
            user_info_cache['librarypwd'] = auth_info.librarypwd
            return user_info_cache
        else:
            return False


def set_user_realname_and_classname(openid):
    """
    写入用户的真是姓名和班级
    """
    redis_prefix = "wechat:user:"
    user_info_cache = redis.hgetall(redis_prefix + openid)
    realname_exists = redis.hexists(redis_prefix + openid, 'realname')

    if not realname_exists or user_info_cache['realname'] != realname.encode('utf-8'):
        user_info = WechatUser.query.filter_by(openid=openid).first()
        if user_info:
            user_info.realname = realname
            user_info.classname = classname
            user_info.update()
        #  写入缓存
        redis.hmset(redis_prefix + openid, {
            "realname" : realname,
            "classname" : classname
        })

