# !/usr/bin/env python
# _*_ coding:utf-8


from app import db
from datetime import datetime
from app.models import registrations


class WechatUser(db.Model):
    __tablename__ = 'wechatusers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(32), unique=True, nullable=False)
    nickname = db.Column(db.String(32), nullable=True)
    realname = db.Column(db.String(32), nullable=True)
    classname = db.Column(db.String(32), nullable=True)
    sex = db.Column(db.SmallInteger, default=0, nullable=False)
    province = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(20), nullable=True)
    headimgurl = db.Column(db.String(150), nullable=True)
    regtime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_setting = db.Column(db.String(100))

    user_group = db.relationship('Group', secondary=registrations,
            backref = db.backref('wechatusers', lazy='dynamic'),
            lazy = 'dynamic')

    #  phone_number = db.Column(db.String(32), nullable=True)
    #  eamil = db.Column(db.String(32), nullable=True)

    def __init__(self, openid, nickname=None, realname=None,
            classname = None, sex = None, province = None, city = None,
            country = None, headimgurl = None, regtime = None):
        self.openid = openid
        self.nickname = nickname
        self.realname = realname
        self.classname = classname
        self.sex = sex
        self.province = province
        self.city = city
        self.country = country
        self.headimgurl = headimgurl
        self.regtime = regtime

    def __repr__(self):
        return '<openid %r>' % self.openid

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self

    #  FIXME  自动分组
    @staticmethod
    def on_created(target, value, oldvalue, initiator):
        group = Group.query.filter_by(name='全体用户').first()
        if group is None:
            new_group = Group()
            new_group.name = '全体用户'
            #  user.user_group.append(new_group)
        else:
            target.user_group = Group.query.filter_by(name='全体用户').first()

#  数据库on_created事件监听 #  每插入新对象就初始化用户的user_group
db.event.listen(WechatUser.openid, 'set', WechatUser.on_created)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    pushnews= db.relationship('Pushnews', backref='to_group')
    pushtext = db.relationship('Pushtext', backref='to_group')

    @staticmethod
    def seed():
        #  XXX  调用这个方法就可以设置Role的默认值了, 这个可以去掉了
        db.session.add_all(map(lambda r:Group(name=r), ['全体用户', '就业信息', '学术报告']))
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self

