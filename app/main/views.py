# coding :utf-8
from flask import flash, session, request, Response, render_template, url_for, redirect, abort, current_app,g, jsonify
from os import path
from . import main
from .. import db
from ..models import User, Role
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, SearchForm
from ..config import DevelopmentConfig as config
from sqlalchemy import extract, func
from datetime import datetime

from app.wechat.func_plugins import wechat_custom
from app.wechat.utils import init_wechat_sdk, delete_dir


basepath = path.abspath(path.dirname(__file__))

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    return redirect(url_for('wechat.user'))


#  @app.route('/user/<int: user_id>')
#  @app.route('/user/<regex("[a-z]+"):name>')
@main.route('/user/<name>')
def user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


#  定义一个装饰器, 修饰只有管理员才能访问的路由
from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_user.is_administrator():
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorator


#  把输入框的字串用, 分开, 然后转化为category对象，现在已经没用了
def str_to_obj(new_category):
    c =[]
    for category in new_category:
        category_obj=Category.query.filter_by(name=new_category).first()
        if category_obj is None:
            category_obj = Category(name=new_category)
            c.append(category_obj)
    return category_obj


@main.route('/about')
def about():
    return render_template('about.html', title='M-Kepler | ABOUT')

@main.route('/search', methods=['GET', 'POST'])
def search():
    return 'test'


@main.before_app_request
def before_request():
    #  if current_user.is_authenticated: #  全文搜索,让这个搜索框
    g.search_form = SearchForm()


@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.name.data:
            current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('你的资料已更新.')
        return redirect(url_for('.user', name=current_user.name))
    form.name.date = current_user.name
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)


@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('You Profile has been updated.')
        return redirect(url_for('.user', name=user.name))
    form.email.data = user.email
    form.name.data = user.name
    form.confirmed.data = user.confirmed
    form.role.data = user.role.name
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form = form, user=user)


@main.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, e=e), 404


@main.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', code=500, e=e), 500
