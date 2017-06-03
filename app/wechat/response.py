# coding:utf-8

#  [对点击菜单/文字等] 的回复处理都放在这里.
#  而回复的具体功能实现放在func_plugins里


import re
from .models.auth import Auth
from .models.user import WechatUser
from wechatpy import parse_message, create_reply, events
from wechatpy import WeChatClient
from wechatpy.replies import TransferCustomerServiceReply
from flask import current_app as app
from .func_plugins import wechat_custom, music, score, weather, school_news, message_confirmed
from .models import set_user_info, get_user_student_info
from .func_plugins.state import get_user_last_interact_time, set_user_last_interact_time
from .utils import AESCipher, init_wechat_sdk


def handle_wechat_response(data):
    """ 回复微信的POST请求 """
    global msg, openid, wechat_client
    wechat_client = WeChatClient(app.config['APPID'],app.config['APPSECRET'])
    msg = parse_message(data)
    openid = msg.source
    #  将用户信息写入数据库
    set_user_info(openid)
    try:
        #  根据消息类型(key值)选择回复方法
        response = msg_type_resp[msg.type]()
    except KeyError:
        #  默认回复消息
        response = 'success'
    #  保存最后一次交互时间
    set_user_last_interact_time(openid, msg.time)
    return response


#  存储微信的消息类型 or 事件的字典
msg_type_resp = {}
msg_event_resp = {}


def set_msg_type(msg_type):
    """ 根据消息类型对应函数的装饰器 """
    def decorator(func):
        msg_type_resp[msg_type] = func
        return func
    return decorator


def set_msg_event(msg_event):
    """ 根据消息事件对应函数的装饰器 """
    def decorator(func):
        msg_event_resp[msg_event] = func
        return func
    return decorator


@set_msg_type('event')
def response_event():
    """ 订阅回复 """
    try:
        get_event_respon_func = msg_event_resp[msg.event]
        event_response = get_event_respon_func()
    except KeyError:
        #  默认回复消息
        event_response = 'success'
    return event_response


@set_msg_type('text')
def response_text():
    """ 回复文本类型消息
    根据用户发的文字调用特定的功能
    """
    commands= {
        u'^绑定': auth_url,
        u'^天气': get_weather,
        u'^新闻': get_school_news,
        u'^游戏': html5_games,
        u'^收到' : confirmed,
        u'^更新菜单': update_menu_setting,
        u'\?|^？|^help|^帮助': all_command
            }
    #  匹配指令
    command_match = False
    for key_word in commands:
        if re.match(key_word, msg.content):
            response = commands[key_word]()
            command_match = True
            break
    if not command_match:
        response = command_not_found()
    return response


@set_msg_type('location')
def response_location():
    location_x = msg.location_x
    location_y = msg.location_y
    #  get_weather(openid, location_x, location_y)
    return create_reply('收到位置信息，经度%s, 纬度%s ' % (location_x, location_y), msg).render()


@set_msg_type('image')
def response_image():
    """ 回复图片消息 """
    media_id = ''
    reply = create_reply(media_id, msg)
    return reply.render()


#  XXX 没办法 wechatpy 没有对tpye和event统一, 我只能这样了
@set_msg_event('subscribe')
def response_subscribe():
    """ 回复订阅事件 """
    content = app.config['WELCOME_TEXT'] + app.config['COMMAND_TEXT']
    reply = create_reply(content, msg)
    return reply.render()


@set_msg_event('click')
def response_click():
    """ 回复菜单的点击事件 """
    commands= {
            'random_music' : play_random_music,
            'school_news' : get_school_news,
            'auth' : auth_url,
            'help' : all_command,
            'score' : exam_grade,
            'setting' : setting,
            'weather': get_weather
            }
    response = commands[msg.key]()
    return response


def auth_url():
    """ 教务系统\图书馆绑定的url """
    auth_info = Auth.query.filter_by(openid=openid).first()
    user_info = WechatUser.query.filter_by(openid=openid).first()
    if not auth_info:
        #  组装url
        jw_url = app.config['HOST_URL'] + '/auth-score/' + openid
        library_url = app.config['HOST_URL'] + '/auth-library/' + openid
        content = app.config['AUTH_TEXT'] % (jw_url)
        reply = create_reply(content, msg)
        return reply.render()
    else:
        #  FIXME 返回个人信息
        #  解析13003601插入个人信息表
        reply = create_reply('已绑定学号：%s！\n姓名：%s\n班级：%s' % (auth_info.studentid, user_info.realname,
            user_info.classname), msg)
        return reply.render()



def command_not_found():
    """ 非关键字回复
    # TODO 后台转接客服
    """
    if(msg.content.startswith("歌曲")):
        music_title= msg.content.replace("歌曲", "")
        if "" == music_title:
            content = "搜索歌曲名称不能为空\nTips：'歌曲'+'歌名'+'歌手'(如：歌曲遇见孙燕姿)"
            reply = create_reply(content, msg)
            return reply.render()
        else:
            play_music(music_title)
        return 'success'
    else:
        content = app.config['COMMAND_NOT_FOUND'] + app.config['HELP_TEXT']
        reply = create_reply(content, msg)
        return reply.render()


'''
def command_not_found():
    """ 非关键字回复
    """
    #  转接客服接口回复信息
    content = app.config['COMMAND_NOT_FOUND'] + app.config['HELP_TEXT']
    wechat_custom.send_text(openid, content)
    #  转发到微信多客服系统
    return TransferCustomerServiceReply()
'''


def all_command():
    """ 回复全部指令 """
    content = app.config['COMMAND_TEXT']
    reply = create_reply(content, msg)
    return reply.render()



def update_menu_setting():
    """ 更新自定义菜单
    #  TODO 只要在后台回复'更新菜单'就行了...看来我得加个权限啊
    """
    try:
        wechat_client.menu.create(app.config['MENU_SETTING'])
    except Exception as e:
        return create_reply(e, msg).render()
    else:
        return create_reply('Done!', msg).render()


def developing():
    """ 维护公告 """
    return create_reply('该功能正在维护中...', msg).render()


def confirmed():
    """ 确认通知已经收到 """
    try:
        content=message_confirmed.confirmed(openid)
        reply = create_reply(content, msg)
        return reply.render()
    except Exception as e:
        app.logger.warning('消息确认出错')
    return 'success'


def play_music(music_title):
    """ 搜索网易云音乐 """
    music.query_music(openid, music_title)
    return 'success'


def play_random_music():
    """ 随机豆瓣FM音乐 """
    music.get_douban_fm(openid)
    return 'success'


def get_school_news():
    """ 学校新闻 """
    school_news.get(openid)
    return 'success'


def html5_games():
    """ html5游戏 """
    content = app.config['HTML5_GAMES'] + app.config['HELP_TEXT']
    return create_reply(content, msg).render()


def get_weather():
    """ 获取天气信息 """
    weather.get(openid)
    return 'success'


def setting():
    """ 自定义订阅消息类型 """
    setting_url = app.config['HOST_URL'] + '/setting/' + openid
    #  setting_url = app.config['HOST_URL'] + '/setting'
    content = '<a href = "%s">【点击进入公众号消息设置】</a>' % setting_url
    reply = create_reply(content, msg)
    return reply.render()


def exam_grade():
    """查询成绩
    """
    user_student_info = get_user_student_info(openid)
    if user_student_info:
        #  解密密码
        cipher = AESCipher(app.config['PASSWORD_SECRET_KEY'])
        studentpwd = cipher.decrypt(user_student_info['studentpwd'])
        score.get_info(openid, user_student_info['studentid'], studentpwd)
        return create_reply('查询完成', msg).render()
    else:
        url = app.config['HOST_URL'] + '/auth-score/' + openid
        content = app.config['AUTH_JW_TEXT'] % url
        reply = create_reply(content, msg)
        return reply.render()


