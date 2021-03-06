# coding:utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:159357@localhost:3306/wechat?charset=utf8"
    PER_POSTS_PER_PAGE=8


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
    #  SAVEPIC='/home/kepler/wx_images/upload_mass_images'
    SAVEPIC='~/workspaces/wechat/wx_images/upload_mass_images'


class TestingConfig(Config):
    TESTING = True


class WechatConfig(Config):
    MYOPENID = 'oApGExFBMSuX7JogXTMYdj9SGlyg'
    APPID = 'wx1638afb292624d0a'
    APPSECRET = '3436a11a7f5fd3d2c1225967e5aeb049'
    TOKEN = "kepler"
    REDIRECT_URI = 'http://huangjinjie.ngrok.cc/wechat/setting'
    #  REDIRECT_URI = 'http://huangjinjie.me/wechat/setting'

    #  素材库图片ID
    MUSIC_THUMB_MEDIA_ID='bad_N1NZTEv_2maH7LQ6CJ8ZBCjrB6AAroHPzCIzGro'

    #  通知的封面ID
    NEWS_THUMB_MEDIA_ID = 'bad_N1NZTEv_2maH7LQ6CEl8yzbTAU0zh8scpIyC6zw'
    NEWS_AUTHOR = ''
    NEWS_DIGEST = "阅读后请后台回复'收到'"
    NEWS_CONTENT_SOURCE_URL = 'http://www.guet.edu.cn'

    EncodingAESKey = " "

    WELCOME_TEXT = "欢迎关注我的公众号.\n"
    HOST_URL = "http://huangjinjie.ngrok.cc/wechat"
    #  HOST_URL = "http://huangjinjie.me/wechat"

    COMMAND_TEXT = "您可以回复以下关键字:\n---------------\n天气  新闻  歌曲\n游戏  测试5  测试6"
    COMMAND_NOT_FOUND = "\n后台已收到您的留言!"
    HELP_TEXT = u"\n\n回复' ? '查看帮助信息\n"
    HTML5_GAMES = u'<a href="http://autobox.meiriq.com/list/302da1ab?from=gxgkcat">开始玩游戏：点击这里</a>'
    BAIDU_ANALYTICS = ""
    SCHOOL_LAN_PROXIES = ""
    PASSWORD_SECRET_KEY = "HardToGuessKeys."

    #  绑定认证URL
    AUTH_JW_TEXT = '\n<a href = "%s">【未绑定？点击这里绑定学号】</</a>\n'
    AUTH_LIBRARY_TEXT = '\n<a href = "%s">【未来绑定？点击这里绑定图书馆帐号】</</a>\n'
    AUTH_TEXT = '\n<a href="%s">教务系统绑定：点击这里</a>\n'
    JW_LOGIN_URL = "http://bkjw2.guet.edu.cn/student/public/login.asp"
    JW_SCORE_URL = "http://bkjw2.guet.edu.cn/student/Score.asp"
    JW_INFO_URL = 'http://bkjw2.guet.edu.cn/student/Info.asp'
    JW_LOGIN_URL_LAN = ""
    JW_SCORE_URL_LAN = ""
    SCHOOL_NEWS_URL = "http://www.guet.edu.cn/ExtGuetWeb/News?stype=1"
    CONFIRMED_WARNNING = "【通知：%s\n（收到通知请回复'收到'）】"

    #  每次修改都要更新菜单
    MENU_SETTING = {
        "button": [
            {
                "name" : "引导",
                "sub_button" : [
                    {
                        "type" : "click",
                        "name" : "使用帮助",
                        "key" : "help"
                    },
                    {
                        "type" : "click",
                        "name" : "绑定信息",
                        "key" : "auth"
                    },
                    {
                        "type" : "click",
                        "name" : "消息设置",
                        "key" : "setting"
                    }
                ]
            },

            {
                "name" : "校园直达",
                "sub_button" : [
                    {
                        "type" : "click",
                        "name" : "学校新闻",
                        "key" : "school_news"
                    },
                    {
                        "type" : "view",
                        "name" : "桂电官网",
                        "url" : "http://www.guet.edu.cn"
                    },
                    {
                        "type" : "click",
                        "name" : "期末成绩",
                        "key" : "score"
                    },
                    {
                        "type" : "view",
                        "name" : "常用电话",
                        "url" : HOST_URL + '/phonenumber'
                    }
                ]
            },

            {
                "name":"生活",
                "sub_button":[
                    {
                        "type":"click",
                        "name":"随机音乐",
                        "key" :"random_music"
                    },
                    {
                        "type":"click",
                        "name":"天气预报",
                        "key" :"weather"
                    }
                ]
            }
        ]
    }



config = {
        'development' : DevelopmentConfig,
        'testing' : TestingConfig,
        'default' : DevelopmentConfig,
        'wechat' : WechatConfig
        }

