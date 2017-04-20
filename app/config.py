# coding:utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    PER_POSTS_PER_PAGE=8
    #  @staticmethod
    #  def init_app(app):
        #  pass


class DevelopmentConfig(Config):
    DEBUG = True
    #  从系统环境变量设置
    #  export MAIL_SERVER = 'test'
    #  查看是否设置成功: echo $MAIL_SERVER
    #  敏感信息从系统环境变量引入
    MAIL_POST = 25
    MAIL_SERVER = 'smtp.qq.com' #  MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_USERNAME = 'm_kepler@foxmail.com' #  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = 'xvildlkqqkklbbbj' #  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASK_MAIL_SUBJECT_PREFIX='M_KEPLER'
    FLASK_MAIL_SENDER=MAIL_USERNAME
    MAIL_PORT=25
    MAIL_USE_TLS=True
    MAIL_DEBUG = True
    ENABLE_THREADS=True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:159357@localhost:3306/keplerblog?charset=utf8"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:159357@localhost:3306/micblog"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:159357@localhost:3306/micblog"


class WechatConfig(Config):
    WELCOME_TEXT = "欢迎关注我的公众号.\n"
    HOST_URL = "http://huangjinjie.ngrok.cc/wechat"
    COMMAND_TEXT = "您可以回复以下关键字:\n-------------\n测试1  测试2  测试3\n测试4  测试5  测试6"
    COMMAND_NOT_FOUND = "后台已收到您的留言!"
    HELP_TEXT = u"\n\n回复' ? '查看主菜单"

    AUTH_JW_TEXT = '<a href = %s">[点击这里绑定学号]</a>\n'
    AUTH_LIBRARY_TEXT = '<a href = %s">[点击这里绑定图书馆帐号]</a>\n'
    AUTH_TEXT = '\n<a href="%s">教务系统绑定：点击这里</a>\n\n<a href="%s">不打算做的绑定图书馆帐号</a>\n'

    MENU_SETTING = {
        "button": [
            {
                "name" : "引导",
                "sub_button" : [
                    {
                        "type" : "view",
                        "name" : "学校主页",
                        "url" : "http://www.guet.edu.cn",
                        "sub_button" : []
                    },
                    {
                        "type" : "click",
                        "name" : "帮助",
                        "key" : "help",
                        "sub_button" : []
                    }
                ]
            },

            {
                "name" : "菜单二",
                "sub_button" : [
                    {
                        "type" : "click",
                        "name" : "学校新闻",
                        "key" : "school_news",
                        "sub_button" : []
                    },
                ]
            }

        ]
    }



config = {
        'development' : DevelopmentConfig,
        'testing' : TestingConfig,
        'production' : ProductionConfig,
        'default' : DevelopmentConfig,
        'wechat' : WechatConfig
        }

