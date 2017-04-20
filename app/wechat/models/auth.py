# !/usr/bin/env python
# _*_ coding:utf-8
"""
    保存用户的教务系统和图书馆的帐号信息
    #  DONE
"""


from app import db


class Auth(db.Model):
    __tablename__ = 'auth'

    openid = db.Column(db.String(32), primary_key=True, unique=True,
            nullable = False)
    studentid = db.Column(db.String(20), nullable=True)
    studentpwd = db.Column(db.String(70), nullable=True)
    libraryid = db.Column(db.String(20), nullable=True)
    librarypwd = db.Column(db.String(70), nullable=True)

    def __init__(self, openid, studentid=None, studentpwd=None,
            libraryid=None, librarypwd=None):
        """
        :openid: 微信用户唯一id
        :studentid: 学生教务系统帐号
        :studentpwd: 学生教务系统密码
        :libraryid: 图书馆帐号
        :librarypwd: 图书馆密码
        """
        self.openid = openid
        self.studentid = studentid
        self.studentpwd = studentpwd
        self.libraryid = libraryid
        self.librarypwd = librarypwd

    def __repr__(self):
        return '<openid %r>' % self.openid

    def save(self):
        db.session.add(self)
        #  我在配置哪里写了自动commit, 这里应该是可以不commit的
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self
