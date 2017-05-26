# !/usr/bin/env python
# _*_ coding:utf-8
#  教务系统绑定 and  成绩查询


import re
import requests
import ast
import time
import random
from flask import current_app
from app import redis
from bs4 import BeautifulSoup, SoupStrainer
from ..models import set_user_student_info, set_user_realname_and_classname, set_user_group
from ..utils import AESCipher, init_wechat_sdk
from . import wechat_custom
from wechatpy import parse_message, create_reply, events

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]



def get_info(openid, studentid, studentpwd, check_login=False):
    """ 登录教务系统, 并保存必要信息"""
    redis_prefix = "wechat:user:score:"
    redis_auth_prefix = "wechat:user:auth:score:"
    user_score_cache = redis.get(redis_prefix + openid)
    if user_score_cache and not check_login:
        #  数据类型转换(把字符串转换成字典)
        content = ast.literal_eval(user_score_cache.decode())
        wechat_custom.send_news(openid, content)

    else:
        # 缓存不存在成绩信息, 建立会话, 模拟登录爬取信息
        session = requests.Session()
        session.headers.update({
            'User-Agent':random.choice(USER_AGENTS),
            'Content-Type':'application/x-www-form-urlencoded',
            'Referer':current_app.config['JW_LOGIN_URL']
            })
        # 登录获取 cookie
        proxy = False
        login_url = current_app.config['JW_LOGIN_URL']
        score_url = current_app.config['JW_SCORE_URL']
        try:
            res = login(studentid, studentpwd, login_url, session, proxy)
        except Exception as e:
            # 外网查询超时，切换内网代理查询
            current_app.logger.warning(u'外网查询出错：%s' % e)
            proxy = True
            login_url = current_app.config['JW_LOGIN_URL_LAN']
            score_url = current_app.config['JW_SCORE_URL_LAN']
            session.headers.update({'Referer': login_url})
            try:
                res = login(studentid, studentpwd, login_url, session, proxy)
            except Exception as e:
                current_app.logger.warning(u'内网查询出错：%s' % e)
                res = None

        #  登录没东西返回可判定为超时
        if not res:
            if check_login:
                errmsg = u"教务系统连接超时，请稍后重试"
                redis.set(redis_auth_prefix + openid, errmsg, 20)
            else:
                content = u"教务系统连接超时\n\n请稍后重试"
                wechat_custom.send_text(openid, content)

        #  登录失败返回200
        elif res.status_code == 200 and 'alert' in res.text:
            if check_login:
                errmsg = u"用户名或密码不正确"
                redis.set(redis_auth_prefix + openid, errmsg, 20)
            else:
                url = current_app.config['HOST_URL'] + '/auth-score/' + openid
                content = u'用户名或密码不正确\n\n' +\
                    u'<a href="%s">点这里重新绑定学号</a>' % url +\
                    u'\n\n绑定后重试操作即可'
                wechat_custom.send_text(openid, content)

        #  否则就是登录成功, 顺便保存相关信息
        else:
            try:
                score_res = score_page(score_url, session, proxy)
                score_res.encoding = 'GBK'
                # 解析 HTML 内容
                soup = BeautifulSoup(score_res.text, "html.parser")
            except Exception as e:
                current_app.logger.warning(u'登录成功，但是在校成绩查询或解析出错：%s,%s' % (
                    e, score_url))
                if check_login:
                    errmsg = u"教务系统连接超时，请稍后重试"
                    redis.set(redis_auth_prefix + openid, errmsg, 20)
                else:
                    content = u"学校的教务系统连接超时\n\n请稍后重试"
                    wechat_custom.send_text(openid, content)
            else:
                # 保存用户真实姓名和所在班级信息
                info_url = current_app.config['JW_INFO_URL']
                try:
                    info_res = session.get(info_url)
                    info_res.encoding = 'GBK'
                    pattern = re.compile(r'<p>(.*?)</p>')
                    items = re.findall(pattern, info_res.text)
                except Exception as e:
                    current_app.logger.warning('登录成功, 但获取个人信息出错')
                else:
                    realname = items[1][3:]
                    classname = items[2][3:]
                    #  school_term = items[4][3:]
                    #  TODO 最后的时候把这个改回来
                    school_term = '2016-2017_2'
                    set_user_realname_and_classname(openid, realname, classname)
                    #  默认根据班级分组
                    set_user_group(openid, classname)

                # 提取当前学期的成绩
                content = u''
                score_info = []
                for idx, tr in enumerate(soup.find_all('tr')[:-1]):
                    if idx != 0:
                        tds = tr.find_all('td')
                        term = tds[0].contents[0]
                        lesson_name = tds[1].contents[0]
                        score = tds[3].contents[0]
                        if term == school_term:
                            # 组装当前学期成绩文本格式数据回复用户
                            content = content + u'课程名称：%s\n考试成绩：%s\n\n' % (lesson_name, score)
                            score_info.append({"term":term, "lesson_name": lesson_name, "score":score})
                        else:
                            # 组装所有学期成绩数组格式的数据备用
                            score_info.append({"term":term, "lesson_name": lesson_name, "score": score})

                # 查询不到成绩
                if not content:
                    content = u'抱歉，没查询到结果, 可能还没公布成绩\n请稍候查询'
                    wechat_custom.send_text(openid, content)
                else:
                    url = current_app.config['HOST_URL'] + '/score-report/' + openid
                    data = [{
                        'title': u'%s - %s学期成绩 ' % (realname, school_term),
                        'description':'',
                        'url':url
                    }, {
                        'title':content,
                        'description':'',
                        'url':url
                    }, {
                        'title':'点击查看全部学期的成绩',
                        'description':'',
                        'url':url
                    } ]

                    # 缓存结果 1 小时
                    redis.set(redis_prefix + openid, data, 3600)
                    #  发送微信
                    wechat_custom.send_news(openid, data)

                    # 更新缓存成绩，用于 Web 展示，不设置过期时间
                    redis.hmset('wechat:user:scoreforweb:' + openid, {
                        "real_name" : realname,
                        "school_term" : school_term,
                        "score_info" : score_info,
                        "update_time" : time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                # 账号密码保存数据库
                if check_login:
                    # 加密密码
                    cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
                    studentpwd = cipher.encrypt(studentpwd)
                    set_user_student_info(openid, studentid, studentpwd)
                    redis.set(redis_auth_prefix + openid, 'ok', 20)


def login(studentid, studentpwd, url, session, proxy):
    """ 登录获取 cookie
    登录成功之后，教务系统会返回 302 跳转
    """
    if not proxy:
        pre_login = session.get(url, allow_redirects=False, timeout=5)
    else:
        pre_login = session.get(url, allow_redirects=False, timeout=5,
                proxies= current_app.config['SHOOL_LAN_PROXIES'])
    pre_login.raise_for_status() # 返回错误状态码
    #  模拟登录所需信息
    payload = {
            'username':studentid,
            'passwd':studentpwd,
            'login':'%B5%C7%A1%A1%C2%B2'
            }
    if not proxy:
        result = session.post(url, data=payload, allow_redirects=False,
                timeout=5)
    else:
        result = session.post(url, data=payload, allow_redirects=False,
                timeout=5, proxies= current_app.config['SCHOOL_LAN_PROXIES'])
    return result


def score_page(score_url, session, proxy):
    """ 在校成绩页面 """
    payload = {
            'ckind' : '',
            'lwPageSize' : '1000',
            'lwBtnquery' : '%B2%E9%D1%AF'
            }
    if not proxy:
        score_res = session.post(score_url, data=payload, allow_redirects=False,
                timeout=5)
    else:
        score_res = session.post(score_url, data=payload, allow_redirects=False,
                proxies=current_app.config['SCHOOL_LAN_PROXIES'],
                timeout=5)
    return score_res


