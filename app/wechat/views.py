# !/usr/bin env python
# coding:utf-8
from flask import flash, session, request, render_template, url_for,\
        redirect, abort, current_app, g, jsonify, Markup
from . import wechat
from app import redis
from .utils import check_wechat_signature, get_jsapi_signature_data, oauth_request, openid_list
from .response import handle_wechat_response
from .func_plugins import score
from .models import is_user_exists
from .models.user import WechatUser, Group
from .form import GroupForm
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
@oauth_request
@wechat.route('/setting/<openid>', methods=['GET', 'POST'])
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
    """ 用户列表
    """
    users = WechatUser.query.all()
    #  group_value = ",".join([i.name for i in user.user_group])
    return render_template('wechat/user.html', users=users)


@wechat.route('/edit')
def editpost(id=0):
    form = PostForm()
    if id == 0: # 新增, current_user当前登录用户
        post = Post(author_id = current_user.id)
    else:
        post = Post.query.get_or_404(id)

    if form.validate_on_submit():
        categoryemp = []
        category_list = form.category.data.split(',')
        # 如果已经有这个分类就不用创建
        for t in category_list:
            tag = Category.query.filter_by(name=t).first()
            if tag is None:
                tag = Category()
                tag.name = t
                #  tag.save()
            categoryemp.append(tag)
        post.categorys = categoryemp
        post.title = form.title.data
        post.body = form.body.data

        post.private = form.private.data
        post.read_count = 0

        db.session.add(post)
        db.session.commit()
        db.session.rollback()
        return redirect(url_for('.post', id=post.id))

    form.title.data = post.title
    #  form.body.data = post.body
    body_value= post.body

    #  form.category.data = [i.name for i in post.categorys]
    #  value = [i.name for i in post.categorys]
    # TODO ☆ 为了把值传到input标签,我也没其他方法了, 然后将category的list元素用‘,’分割组成str传给input

    value = ",".join([i.name for i in post.categorys])

    mode='编辑' if id>0 else '添加'
    return render_template('posts/edit.html', title ='%s - %s' % (mode, post.title), form=form,
            post=post, value=value, body_value = body_value)


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


@wechat.route('/push')
def push():
    return render_template('wechat/push_text.html')


@wechat.errorhandler(404)
def page_not_found(e):
    return '404, PAGE NOTE FOUND!'


