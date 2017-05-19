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

    #  TODO 自动分组
    @staticmethod
    def on_created(target, value, oldvalue, initiator):
        target.role= Role.query.filter_by(name='全体用户').first()


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    pushnews= db.relationship('Pushnews', backref='to_group')
    pushtext = db.relationship('Pushtext', backref='to_group')

    @staticmethod
    def seed(): #  调用这个方法就可以设置Role的默认值了
        #  db.session.add_all(map(lambda r:Role(name=r), ['guests', 'administrators']))
        db.session.add_all(map(lambda r:Group(name=r), ['全体用户']))
        db.session.commit()


