# !/usr/bin env python
# coding:utf-8

import ast, time, json
from os import path
from datetime import datetime
from flask import flash, session, request, render_template, url_for,\
        redirect, abort, current_app, g, jsonify, Markup
from flask_login import login_required, current_user
from sqlalchemy import extract, func
from app import redis, db
from . import wechat
from .response import handle_wechat_response
from .func_plugins import score
from .models import is_user_exists
from .models.user import WechatUser, Group
from .models.pushpost import Pushnews, Pushtext
from .form import GroupForm, NewsForm, TextForm
from .utils import check_wechat_signature, get_jsapi_signature_data,\
        oauth_request, openid_list, init_wechat_sdk

from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_user.is_administrator():
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorator


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
        errmsg_cache = redis.get(redis_prefix + openid)
        errmsg = errmsg_cache.decode()
        if errmsg:
            #  redis.delete(redis_prefix + openid)
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


    """ 修改用户分组 """
    if form.validate_on_submit():
        groupemp = []
        groupemp_list = form.group.data.split(',')
        for t in groupemp_list:
            tag = Group.query.filter_by(name=t).first()
            if tag is None:
                tag = Group()
                tag.name = t
            groupemp.append(tag)
        user.user_group = groupemp
        user.save()
        return redirect(url_for('wechat.user'))
    value = ",".join([i.name for i in user.user_group])
    return render_template('wechat/editgroup.html',form=form, user=user, value=value)


#  不用oauth授权的话, 只能传openid参数了
#  @wechat.route('/setting/<openid>', methods=['GET', 'POST'])
#  @oauth_request
@wechat.route('/setting/<openid>', methods=['GET', 'POST'])
def setting(openid=None):
    user = WechatUser.query.filter_by(openid=openid).first()
    if request.method == 'POST':
        #  只是保存了用户的设置的一个列表
        setting_list = request.form.getlist('setting')

        #  根据设置给用户分组
        for i in setting_list:
            group = Group.query.filter_by(name=i).first()
            if group not in user.user_group:
                if group is None:
                    new_group = Group()
                    new_group.name = i
                    user.user_group.append(new_group)
                else:
                    user.user_group.append(group)
            user.update()

        #  用户去掉某个选择的时候, 就是比对数据库的user_setting和从网页传回来的setting_list
        user_setting_list = json.loads(user.user_setting)
        for i in user_setting_list:
            if i not in setting_list:
                delete_group = Group.query.filter_by(name=i).first()
                user.user_group.remove(delete_group)
        user.user_setting = json.dumps(setting_list)
        user.update()

        #  TODO 显示一个Toast后, 关闭窗口
        return 'success'
    else:
        if user.user_setting:
            setting_list = json.loads(user.user_setting)
            setting_list = ','.join(setting_list)
        else:
            setting_list = []
        return render_template('wechat/setting.html', values = setting_list)


@wechat.route('/setting/result', methods=['GET'])
def setting_result(openid=None):
    """ 查询学号绑定结果 """
    user = WechatUser.query.filter_by(openid=openid).first()
    if user.user_setting:
        return jsonify({'errmsg' : ok})
    else:
        return jsonify({'errmsg' : '保存出错'})


@wechat.route('/phonenumber', methods=['GET'])
def phone_number():
    """ 回复常用电话 """
    return render_template('wechat/phone_number.html')


@wechat.route('/user')
@login_required
def user():
    """ 用户列表 """
    users = WechatUser.query.all()
    groups = Group.query.order_by(Group.id)[::-1] # 所有标签返回的是一个元组
    #  FIXME 该分组下用户数为0, 删除这个分组
    for c in groups:
        p = c.wechatusers.all()
        if len(p) == 0:
            db.session.delete(c)
    return render_template('wechat/user.html', users=users)


@wechat.route('/editgroup/<int:id>', methods = ['GET','POST'])
@login_required
@admin_required
def editgroup(id=0):
    """ 修改用户分组 """
    form = GroupForm()
    user = WechatUser.query.get_or_404(id)
    if form.validate_on_submit():
        groupemp = []
        groupemp_list = form.group.data.split(',')
        for t in groupemp_list:
            tag = Group.query.filter_by(name=t).first()
            if tag is None:
                tag = Group()
                tag.name = t
            groupemp.append(tag)
        user.user_group = groupemp
        user.save()
        return redirect(url_for('wechat.user'))
    value = ",".join([i.name for i in user.user_group])
    return render_template('wechat/editgroup.html',form=form, user=user, value=value)


@wechat.route('/groups/<name>', methods=['GET', 'POST'])
def group(name):
    group = Group.query.filter_by(name = name).first() # name对应的标签对象
    page_index = request.args.get('page', 1, type=int)
    pagination = group.wechatusers.order_by(WechatUser.id.desc()).paginate( page_index, per_page = 8, error_out=False)
    users = pagination.items
    return render_template("wechat/groups.html", name = name, users = users, group = group, pagination=pagination)


@wechat.route('/push', methods=['GET', 'POST'])
@login_required
@admin_required
def push():
    """ 推送图文消息"""
    newsform = NewsForm()
    form = TextForm()
    wechat = init_wechat_sdk()
    client = wechat['client']
    pushnews = Pushnews(author_id = current_user.id)
    if request.method == 'POST':
        #  把推送保存到数据库, 并发送微信
        title = newsform.title.data
        body = newsform.body.data
        to_group = Group.query.get(newsform.group.data)
        to_user = []
        to_user_id = []
        for u in to_group.wechatusers:
            to_user.append(u.openid)
            to_user_id.append(u.id)

        try:
            #  添加到图文素材库
            pushnews.title = title
            pushnews.body = body
            pushnews.to_group = to_group
            pushnews.to_confirmed = json.dumps(to_user_id)
            pushnews.save()
            body_html=pushnews.body_html
            #  更新最新推送的通知缓存
            articles= [{
                'title':title,
                'show_cover_pic' : 0,
                'content':body_html, # 看看是否需要处理html
                'author':current_user.name,
                'thumb_media_id':current_app.config['NEWS_THUMB_MEDIA_ID'],
                'digest':current_app.config['NEWS_DIGEST'],
                'content_source_url':current_app.config['NEWS_CONTENT_SOURCE_URL'],
                'need_open_comment' : '1',
                'only_fans_can_comment' : '1'
            }]
            res = client.material.add_articles(articles)
            #  XXX, 为什么没有保存到数据库, 但却发送成功了
            media_id = res['media_id']
            current_app.logger.warning('添加的图文的media_id: %s' % media_id)
            #  保存到数据库 TODO 多添加几个字段
            pushnews.media_id = media_id
            pushnews.update()
            redis.set("wechat:last_push_time", time.strftime('%Y-%m-%d %H:%M:%S'))
            redis.hmset("wechat:last_push", {
                "create_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
                "to_confirmed" : to_user_id,
                "media_id":media_id,
                "pushtype":'news'
                })
            redis_pushtext_prefix = "wechat:pushnews:" + media_id
            redis.hmset(redis_pushtext_prefix, {
                "media_id" : media_id,
                "to_user" : to_user,
                "create_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
                "to_confirmed" : to_user_id
                })

        except Exception as e:
            print(e)
            current_app.logger.warning('添加图文到数据库和缓存失败')

        try:
            #  发送图文消息
            send_result = client.message.send_mass_article(to_user, media_id)
        except Exception as e:
            print(e)
        return redirect(url_for('wechat.user'))
    body_value = None
    return render_template('wechat/messagepush.html', title = pushnews.title, newsform=newsform, form=form, pushpost=pushnews, body_value = body_value)


@wechat.route('/pushednews', methods=['GET', 'POST'])
@login_required
def pushednews():
    """ 历史推送的图文通知 """
    pushednews = []
    archives = db.session.query(extract('month', Pushnews.create_time).label('month'),
            func.count('*').label('count')).group_by('month').all()
    for archive in archives:
        pushednews.append((archive[0], db.session.query(Pushnews).filter(extract('month', Pushnews.create_time)==archive[0]).all()))
    return render_template("wechat/pushednews.html", title="已推送的图文通知", posts = pushednews)


@wechat.route('/pushednews-detail/<int:id>')
@login_required
def pushednews_detail(id):
    """ 推送的图文通知的详情"""
    pushednews = Pushnews.query.get(id)
    media_id = pushednews.media_id
    wechat = init_wechat_sdk()
    client = wechat['client']
    get_material = client.material.get(media_id)
    url = get_material[0]['url']
    #  url = "www.baidu.com"
    unconfirmed_id = pushednews.to_confirmed
    unconfirmed_name = []
    to_confirmed = json.loads(unconfirmed_id)
    #  把目标用户的id全加入到未确认消息的分组下
    for user_id in to_confirmed:
        user = WechatUser.query.filter_by(id=user_id).first()
        if user.realname:
            unconfirmed_name.append(user.realname)
        else:
            unconfirmed_name.append(user.nickname)
    return render_template('wechat/pushednews_detail.html', unconfirmed_name = unconfirmed_name, url=url, pushednews=pushednews)


@wechat.route('/pushtext', methods=['GET', 'POST'])
@login_required
@admin_required
def pushtext():
    """ 推送文字信息 """
    form = TextForm()
    wechat = init_wechat_sdk()
    client = wechat['client']

    pushtext = Pushtext(author_id = current_user.id)
    content = current_app.config['CONFIRMED_WARNNING'] % form.textarea.data

    group_name = form.group.data
    to_group =  Group.query.get(form.group.data)
    to_user = []
    to_user_id = []
    for u in to_group.wechatusers:
        to_user.append(u.openid)
        to_user_id.append(u.id)
    try:
        send_result = client.message.send_mass_text(to_user, content)
        current_app.logger.warning(u'发送结果：%s' % send_result)
        media_id = send_result['msg_id']
        mass_status = client.message.get_mass(media_id)

        pushtext.content = content
        pushtext.media_id = media_id
        pushtext.to_group =  Group.query.get(form.group.data)
        pushtext.to_confirmed = json.dumps(to_user_id)
        pushtext.save()

        #  保存最新一条推送的时间
        #  FIXME 这两个是不是重复了
        redis.set("wechat:last_push_time", time.strftime('%Y-%m-%d %H:%M:%S'))
        redis.hmset("wechat:last_push", {
            "create_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
            "to_confirmed" : to_user_id,
            "media_id":media_id,
            "pushtype":'text'
            })

        #  保存信息到redis
        redis_pushtext_prefix = "wechat:pushtext:" + media_id
        redis.hmset(redis_pushtext_prefix, {
            "media_id" : media_id,
            "to_user" : to_user,
            "create_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
            "to_confirmed" : to_user_id
            })

        current_app.logger.warning('to_user_list:%s' % to_user)
        current_app.logger.warning(u'发送情况：%s' % mass_status)


    except Exception as e:
        print(e)
    return redirect(url_for('wechat.user'))


@wechat.route('/pushedtext', methods=['GET', 'POST'])
@login_required
def pushedtext():
    """ 历史推送的文本通知 """
    pushedtexts = []
    archives = db.session.query(extract('month', Pushtext.create_time).label('month'),
            func.count('*').label('count')).group_by('month').all()
    for archive in archives:
        pushedtexts.append((archive[0], db.session.query(Pushtext).filter(extract('month', Pushtext.create_time)==archive[0]).all()))
    return render_template("wechat/pushedtext.html", title="已推送的文本通知", posts = pushedtexts)


@wechat.route('/pushedtext-detail/<int:id>')
@login_required
def pushedtext_detail(id):
    """ 推送的文本通知的详情"""
    pushedtext = Pushtext.query.get(id)
    return render_template('wechat/pushedtext_detail.html', pushedtext=pushedtext)



@wechat.route('/pushmetting', methods=['GET', 'POST'])
def pushmetting():
    """ 推送会议
    保存会议的时间地点和会议内容到数据库，更新最新一条推送的信息，
    并把内容发给用户, 其他的和普通推送应该差不多
    """
    pass
    redis.set("wechat:last_push_time", time.strftime('%Y-%m-%d %H:%M:%S'))
    redis.hmset("wechat:last_push", {
        "create_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
        "to_confirmed" : to_user_id,
        "media_id": media_id,
        "pushtype":'metting'
        })



@wechat.route('/upload/',methods=['POST'])
def upload():
    """ 处理图片上传 """
    file=request.files.get('editormd-image-file')
    if not file:
        res={
            'success':0,
            'message':u'图片格式异常'
        }
    else:
        ex=path.splitext(file.filename)[1] # 获取文件扩展名
        filename=datetime.now().strftime('%Y%m%d%H%M%S')+ex # 根据时间戳组装文件名
        file_path = path.join(current_app.config['SAVEPIC'], filename)
        file.save(file_path)
        wechat = init_wechat_sdk()
        client = wechat['client']
        #  把图片上传到本地, 然后上传到微信, 得到url
        with open(path.join(current_app.config['SAVEPIC'], filename),'rb') as f:
            url = client.media.upload_mass_image(f)

        #  delete_dir()
        #  'url':url_for('.image', name = filename)
        res={
            'success':1,
            'message':u'图片上传成功',
            'url':url
        }
    return jsonify(res)


@wechat.errorhandler(404)
def page_not_found(e):
    return '404, PAGE NOTE FOUND!'


