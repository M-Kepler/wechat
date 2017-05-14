# !/usr/bin/env python
# _*_ coding:utf-8

from flask_wtf import FlaskForm as Form
from app.wechat.models.user import Group
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, validators, ValidationError
from wtforms.validators import DataRequired, length, Regexp, EqualTo, Email

class GroupForm(Form):
    group = StringField("设置分组", validators=[DataRequired()])
    submit = SubmitField(('提交'))
