# !/usr/bin/env python
# _*_ coding:utf-8

from flask_wtf import FlaskForm as Form
from flask_pagedown.fields import PageDownField
from app.wechat.models.user import Group
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, validators, ValidationError
from wtforms.validators import DataRequired, length, Regexp, EqualTo, Email

class GroupForm(Form):
    group = StringField("设置分组", validators=[DataRequired()])
    submit = SubmitField(('提交'))


class TextForm(Form):
    group = StringField("发送给分组", validators=[DataRequired()])
    textarea = PageDownField(label=('正文'), validators=[DataRequired()])
    #  is_to_all = BooleanField("发给全部用户")
    submit = SubmitField(('提交'))

    def __init__(self,  *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        self.group.choices=[(group.id, group.name)
                for group in Group.query.order_by(Group.name).all()]


class NewsForm(Form):
    """ 发布 """
    title = StringField(label=('标题'), validators=[DataRequired()])
    group = StringField("发送给分组", validators=[DataRequired()])
    body = PageDownField(label=('正文'), validators=[DataRequired()])
    #  is_to_all = BooleanField("发给全部用户")
    submit = SubmitField(('提交'))

    def __init__(self,  *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.group.choices=[(group.id, group.name)
                for group in Group.query.order_by(Group.name).all()]

