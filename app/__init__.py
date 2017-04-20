# _*_coding:utf-8_*_

from flask import Flask, request
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from os import path
from datetime import datetime
from werkzeug.routing import BaseConverter
from .config import config
import logging
from logging.handlers import RotatingFileHandler
from redis import Redis


#  为路由规则增加正则转换器
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex=items[0]


bootstrap = Bootstrap()
db = SQLAlchemy()
redis = Redis()
#  manager = Manager()
moment=Moment()
mail=Mail()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection='strong'
login_manager.login_view = 'auth.signin'

basedir = path.abspath(path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.url_map.converters['regex'] = RegexConverter
    #  加载配置
    #  app.config.from_pyfile('config.py')
    app.config.from_object(config['default'])
    app.config.from_object(config['wechat'])

    #  初始化第三方库
    moment.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 注册蓝图
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .wechat import wechat as wechat_blueprint

    #  url_prefix(url前缀)加上后就把auth目录下的view注册到蓝图中，不加的话就使用app下的view
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    #  static_fold  指定蓝图的静态文件所在文件夹
    #  app.register_blueprint(main_blueprint, url_prefix='/main', static_fold='static')
    app.register_blueprint(main_blueprint, static_fold='static')
    app.register_blueprint(wechat_blueprint, url_prefix='/wechat')

    @app.template_test('current_link')
    def is_current_link(link):
        return link == request.path

    #  记录运行那个日志
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
        '[in %(pathname)s:%(lineno)d]'
        ))
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)


    return app
