# !/usr/bin/env python
# _*_ coding:utf-8
"""
    用户个人信息
    #  TODO
"""


from app import db
from datetime import datetime


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

    # TODO 我要对用户进行分组, 好像微信提供了分组的接口, 所以我还用写role表吗?
    role_id = db.Column(db.Integer)
    phone_number = db.Column(db.String(32), nullable=True)
    eamil = db.Column(db.String(32), nullable=True)

    def __init(self, openid, nick_name=None, real_name=None,
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

