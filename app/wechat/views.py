# !/usr/bin env python
# coding:utf-8
from flask import flash, session, request, render_template, url_for,\
        redirect, abort, current_app, g, jsonify, Markup
from . import wechat
from app import redis
from .utils import check_wechat_signature, get_jsapi_signature_data
from .response import handle_wechat_response
from .func_plugins import score
from .models import is_user_exists
import ast



@wechat.route('/test')
def test():
    return 'Hi There'


@wechat.route('/', methods=['GET', 'POST'])
@check_wechat_signature
def handle_wechat_request():
    """ 处理微信回复请求 """
    if request.method == 'GET' :
        #  微信接入认证
        return request.args.get('echostr', '')
    else:
        return handle_wechat_response(request.data)


@wechat.route('/auth-score/<openid>', methods=['GET', 'POST'])
def auth_score(openid=None):
    """ 绑定教务系统 """
    if request.method == 'POST':
        studentid = request.form.get('studentid', '')
        studentpwd = request.form.get('studentpwd', '')
        #  根据用户输入的信息, 进行模拟登录
        if studentid and studentpwd and is_user_exists(openid):
            score.get_info(openid, studentid, studentpwd, check_login=True)
            errmsg = 'ok'
        else:
            errmsg = u'学号或密码格式不合法'
        return jsonify({'errmsg': errmsg})
    elif is_user_exists(openid):
        jsapi = get_jsapi_signature_data(request.url)
        jsapi['jsApiList'] = ['hideAllNonBaseMenuItem']
        return render_template('wechat/auth.html',
                title = '微信查成绩',
                desc = "请绑定教务系统",
                username_label = '学号',
                username_label_placeholder = '请输入你的学号',
                password_label_placeholder = '教务系统密码',
                baidu_analyics = current_app.config['BAIDU_ANALYTICS'],
                jsapi = Markup(jsapi)
                )
    else:
        abort(404)


@wechat.route('/auth-score/<openid>/result', methods=['GET'])
def auth_score_result(openid=None):
    """ 查询学号绑定结果 """
    if is_user_exists(openid):
        redis_prefix = 'wechat:user:auth:score:'
        errmsg = redis.get(redis_prefix + openid)
        if errmsg:
            redis.delete(redis_prefix + openid)
            return jsonify({'errmsg' : errmsg})
        else:
            abort(404)
    else:
        abort(404)


@wechat.route('/score-report/<openid>', methods=['GET', 'POST'])
def school_report_card(openid=None):
    """ 学生成绩单 """
    if is_user_exists(openid):
        jsapi = get_jsapi_signature_data(request.url)
        jsapi['jsApiList'] = ['onMenuShareTimeline',
                'onMenuShareAppMessage',
                'onMenuShareQQ',
                'onMenuShareWeibo',
                'onMenuShareQZone']
        score_cache = redis.hgetall('wechat:user:scoreforweb:' + openid)
        if score_cache:
            score_info = ast.literal_eval(score_cache[b'score_info'].decode())
            real_name = score_cache[b'real_name'].decode('utf-8')
            return render_template('wechat/score.html',
                    real_name = real_name,
                    school_term = score_cache[b'school_term'].decode('utf-8'),
                    score_info = score_info,
                    update_time = score_cache[b'update_time'].decode('utf-8'),
                    baidu_analyics= current_app.config['BAIDU_ANALYTICS'],
                    jsapi = Markup(jsapi)
                    )
        else:
            abort(404)
    else:
        abort(404)


@wechat.route('/auth-library/<openid>', methods=['GET', 'POST'])
def auth_library(openid=None):
    """ 绑定图书馆帐号
    XXX 图书馆这个先不做了吧
    """
    if request.method == 'POST':
        libraryid = request.form.get('libraryid', '')
        librarypwd = request.form.get('librarypwd', '')
        if libraryid and librarypwd and is_user_exists(openid):
            errmsg = 'ok'
            pass
        else:
            errmsg = '卡号或密码不正确'


@wechat.route('/auth-library/<openid>/result', methods=['GET'])
def auth_library_result(openid=None):
    """查询借书卡绑定结果"""
    if is_user_exists(openid):
        redis_prefix = 'wechat:user:auth:library:'
        errmsg = redis.get(redis_prefix + openid)
        if errmsg:
            redis.delete(redis_prefix + openid)
            return jsonify({'errmsg': errmsg})
        else:
            abort(404)
    else:
        abort(404)


@wechat.errorhandler(404)
def page_not_found(e):
    return '404, PAGE NOTE FOUND!'


'''
@wechat.errorhandler(Exception)
def unhandled_exception(error):
    current_app.logger.error('Unhandled Exception:%s', (error))
    return "Error", 500
'''


