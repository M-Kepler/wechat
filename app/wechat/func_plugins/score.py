# !/usr/bin/env python
# _*_ coding:utf-8
#  教务系统绑定 and  成绩查询


import re
import requests
import ast
import time
from flask import current_app
from app import redis
from bs4 import BeautifulSoup, SoupStrainer
from ..models import set_user_student_info, set_user_realname_and_classname
from ..utils import AESCipher
from . import wechat_custom


def get_info(openid, studentid, studentpwd, check_login=False):
    """ 登录教务系统, 并保存必要信息"""
    redis_prefix = "wechat:user:score:"
    redis_auth_prefix = "wechat:user:auth:score:"
    user_score_cache = redis.get(redis_prefix + openid)
    if user_score_cache and not check_login:
        #  数据类型转换(把字符串转换成字典)
        #  content = ast.literal_eval(user_score_cache)
        content = eval(user_score_cache)
        wechat_custom.send_news(openid, content)
    else:
        # 缓存不存在成绩信息, 建立会话, 模拟登录爬取成绩
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; ' +
            'Windows NT 6.2; Trident/6.0)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': current_app.config['JW_LOGIN_URL']
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

        #  执行login后未返回信息
        if not res:
            if check_login:
                errmsg = u"教务系统连接超时，请稍后重试"
                redis.set(redis_auth_prefix + openid, errmsg, 10)
            else:
                content = u"教务系统连接超时\n\n请稍后重试"
                wechat_custom.send_text(openid, content)

        #  登录失败返回200
        elif res.status_code == 200 and 'alert' in res.text:
            if check_login:
                errmsg = u"用户名或密码不正确"
                redis.set(redis_auth_prefix + openid, errmsg, 10)
            else:
                url = current_app.config['HOST_URL'] + '/auth-score/' + openid
                content = u'用户名或密码不正确\n\n' +\
                    u'<a href="%s">点这里重新绑定学号</a>' % url +\
                    u'\n\n绑定后重试操作即可'
                wechat_custom.send_text(openid, content)

        # 登录成功, 顺便保存相关信息
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
                    redis.set(redis_auth_prefix + openid, errmsg, 10)
                else:
                    content = u"学校的教务系统连接超时\n\n请稍后重试"
                    wechat_custom.send_text(openid, content)
            else:
                # 提取当前学期的成绩
                content = u''
                score_info = []
                for idx, tr in enumerate(soup.find_all('tr')[:-1]):
                    if idx != 0:
                        tds = tr.find_all('td')
                        term = tds[0].contents[0]
                        lesson_name = tds[1].contents[0]
                        score = tds[3].contents[0]
                        # 组装文本格式数据回复用户
                        content = content + u'\n\n学期：%s\n课程名称：%s\n考试成绩：%s' % (term, lesson_name, score)
                        # 组装数组格式的数据备用
                        score_info.append({"term":term, "lesson_name": lesson_name,
                                           "score": score})

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
                    set_user_realname_and_classname(openid, realname, classname)

                # 查询不到成绩
                if not content:
                    content = u'抱歉，没查询到结果\n可能还没公布成绩\n请稍候查询'
                    wechat_custom.send_text(openid, content)
                else:
                    url = current_app.config['HOST_URL'] + '/score-report/' + openid
                    data = [{
                        'title': u'%s 期末成绩' % realname
                    }, {
                        'title': u'学期%s' % term,
                        'url': url
                    }, {
                        'title': u'点击这里：分享成绩单到朋友圈',
                        'url': url
                    }]
                    # 缓存结果 1 小时
                    redis.set(redis_prefix + openid, data, 3600)
                    #  发送微信
                    wechat_custom.send_news(openid, data)
                    # 更新缓存成绩，用于 Web 展示，不设置过期时间
                    redis.hmset('wechat:user:scoreforweb:' + openid, {
                        "real_name": realname,
                        "school_term": term,
                        "score_info": score_info,
                        "update_time": time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                # 账号密码保存数据库
                if check_login:
                    # 加密密码
                    cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
                    studentpwd = cipher.encrypt(studentpwd)
                    set_user_student_info(openid, studentid, studentpwd)
                    redis.set(redis_auth_prefix + openid, 'ok', 10)


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


