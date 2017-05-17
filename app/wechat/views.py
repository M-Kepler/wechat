# !/usr/bin env python
# coding:utf-8

import ast, time, json
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
from .models.pushpost import Pushpost, Pushtext
from .form import GroupForm, MessagePushForm, TextForm
from .utils import check_wechat_signature, get_jsapi_signature_data,\
        oauth_request, openid_list, init_wechat_sdk


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


#  不用oauth授权的话, 只能传openid参数了
#  @wechat.route('/setting/<openid>', methods=['GET', 'POST'])
#  @oauth_request
@wechat.route('/setting', methods=['GET', 'POST'])
def setting(openid=None):
    if request.method == 'POST':
        #TODO  这个openid_list的值只能设置一次,这里每更改一次这个list都会更改,看看人家怎么实现的
        values = request.form.getlist('check')
        aaaa = openid_list(openid, values)
        print(aaaa)
        return 'success'
    else:
        return render_template('wechat/setting.html')


@wechat.route('/phonenumber', methods=['GET'])
def phone_number():
    """ 回复常用电话 """
    return render_template('wechat/phone_number.html')


@wechat.route('/user')
def user():
    """ 用户列表 """
    users = WechatUser.query.all()
    groups = Group.query.order_by(Group.id)[::-1] # 所有标签返回的是一个元组
    for c in groups:
        p = c.wechatusers.all()
        if len(p) == 0: # 该分类下的文章数为0
            db.session.delete(c)
    return render_template('wechat/user.html', users=users)


@wechat.route('/editgroup/<int:id>', methods = ['GET','POST'])
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
                #  tag.save()
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
def push():
    form = MessagePushForm()
    wechat = init_wechat_sdk()
    client = wechat['client']
    pushpost = Pushpost(author_id = current_user.id)
    if form.validate_on_submit():
        #  把推送保存到数据库, 并发送微信
        pushpost.to_group =  Group.query.get(form.group.data)
        pushpost.title = form.title.data
        pushpost.body = form.body.data
        pushpost.is_to_all = form.is_to_all.data
        #  判断发送类型选择合适的函数
        print(form.is_to_all.data)
        if not form.title.data: #  文字推送
            content = form.body.data
            if not form.is_to_all.data:
                group_name = form.group.data
                print(group_name)
                to_group =  Group.query.filter_by(name=group_name).first()
                to_user = []
                for u in to_group.wechatusers:
                    to_user.append(u.openid)
                current_app.logger.Warning('to_user_list:%s' % to_user)
                try:
                    send_result = client.message.send_mass_text(to_user, content)
                except Exception as e:
                    current_app.logger.warning(u'发送结果：%s' % e)
                    media_id = send_result['msg_id']
                    mass_status = client.message.get_mass(media_id)
                    current_app.logger.warning(u'发送情况：%s' % mass_status)
            else:
                pass
                #  client.message.send_mass_text(content, is_to_all)
                #  推送给全部用户
        else:
            #  图文推送
            print(form.title.data)
        pushpost.save()
        return redirect(url_for('wechat.pushedpost'))

    form.title.data = pushpost.title
    body_value= pushpost.body
    #  value = ",".join([i.name for i in post.categorys])
    return render_template('wechat/messagepush.html', title = pushpost.title, form=form, pushpost=pushpost, body_value = body_value)


@wechat.route('/pushtext', methods=['GET', 'POST'])
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
        redis.set("wechat:last_pushtext_time", time.strftime('%Y-%m-%d %H:%M:%S'))
        redis.hmset("wechat:last_pushtext", {
            "create_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
            "to_confirmed" : to_user_id,
            "media_id":media_id
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
def pushedtext():
    """ 历史推送 """
    pushedtexts = []
    archives = db.session.query(extract('month', Pushtext.create_time).label('month'),
            func.count('*').label('count')).group_by('month').all()
    for archive in archives:
        pushedtexts.append((archive[0], db.session.query(Pushtext).filter(extract('month', Pushtext.create_time)==archive[0]).all()))
    return render_template("wechat/pushedtext.html", title="历史推送", posts = pushedtexts)



@wechat.route('/pushedtext-detail/<int:id>')
def pushedtext_detail(id):
    """ 历史推送信息的详情"""
    pushedtext = Pushtext.query.get(id)
    return render_template('wechat/pushedtext_detail.html', pushedtext=pushedtext)


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


