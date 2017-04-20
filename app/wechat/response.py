# coding:utf-8

import re
from wechatpy import parse_message, create_reply, events
from flask import current_app as app


def handle_wechat_response(data):
    """
    回复微信的POST请求
    """
    global msg, openid
    msg = parse_message(data)
    openid = msg.source
    try:
        #  根据消息类型选择回复方法
        #  TODO: 理解这个用法
        get_response_func = msg_type_resp[msg.type]
        response = get_response_func()
    except KeyError:
        #  默认回复消息
        response = 'success'
    return response


#  存储微信的消息类型/事件的字典
msg_type_resp = {}
msg_event_resp = {}


def set_msg_type(msg_type):
    """
    根据微信消息类型对应函数
    """
    def decorator(func):
        msg_type_resp[msg_type] = func
        return func
    return decorator


def set_msg_event(msg_event):
    """
    根据微信消息类型对应函数
    """
    def decorator(func):
        msg_event_resp[msg_event] = func
        return func
    return decorator


@set_msg_type('event')
def response_event():
    """
    订阅回复
    """
    #  set_user_state(openid, 'default')
    try:
        get_event_respon_func = msg_event_resp[msg.event]
        event_response = get_event_respon_func()
    except KeyError:
        #  默认回复消息
        event_response = 'success'
    return event_response


@set_msg_type('text')
def response_text():
    """
    回复文本类型消息
    """
    #  response = create_reply(msg.content, msg)
    #  这样就可以根据用户发的文字调用特定的功能了
    commands= {
        u'^绑定':auth_url,
        u'\?|^？|^help|^帮助':all_command
            }
    state_commands= {
        'chat':chat_robot
        }

    #  匹配指令
    command_match = False
    for key_word in commands:
        if re.match(key_word, msg.content):
            #  TODO 设置用户状态是什么意思 #  聊天 \ 快递
            #  set_user_state(openid, 'default')
            response = commands[key_word]()
            command_match = True
            break
    if not command_match:
        #  匹配状态
        #  state = get_user_state(openid)
        #  state = 'default'
        #  关键字, 状态都不匹配, 缺省回复
        #  if state == 'default' or not state:
            #  response = command_not_found()
        #  else:
            #  response = state_commands[state]()
        response = command_not_found()
    return response


@set_msg_type('image')
def response_image():
    """
    回复图片消息
    """
    pass


#  XXX 没办法 wechatpy 没有对tpye和event统一, 我只能这样了
@set_msg_event('subscribe')
def response_subscribe():
    """
    回复订阅事件
    """
    content = app.config['WELCOME_TEXT'] + app.config['COMMAND_TEXT']
    reply = create_reply(content, msg)
    return reply.render()


@set_msg_event('click')
def response_click():
    """
    菜单点击事件
    """
    commands= {
            'music' : play_music,
            'weather' : weather,
            'news' :news
            }
    #  set_user_state(openid, 'default')
    reply = commands[msg.key]()
    return reply.render()


@set_msg_event('subscribe_scan')
def response_scan():
    """
    扫码事件
    """
    pass


def auth_url():
    """
    教务系统\图书馆绑定
    """
    jw_url = app.config['HOST_URL'] + '/auth-score/' + openid
    library_url = app.config['HOST_URL'] + '/auth-library/' + openid
    content = app.config['AUTH_TEXT'] % (jw_url, library_url)
    reply = create_reply(content, msg)
    return reply.render()


def command_not_found():
    """
    非关键字指令, 后台留言
    """
    content = app.config['COMMAND_NOT_FOUND'] + app.config['HELP_TEXT']
    reply = create_reply(content, msg)
    return reply.render()


def all_command():
    """
    回复全部指令
    """
    content = app.config['COMMAND_TEXT']
    reply = create_reply(content, msg)
    return reply.render()


def chat_robot():
    """
    聊天机器人接入
    """
    pass
