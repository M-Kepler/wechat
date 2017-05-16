from app import db
from datetime import datetime


class Pushtext(db.Model):
    """ 推送文本消息 """
    __tablename__ = 'pushtexts'
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    to_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class Pushpost(db.Model):
    __tablename__ = 'pushposts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    #  把markdown原文格式成html存到数据库，而不是访问时在格式
    body_html = db.Column(db.Text)
    is_to_all = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))


    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def on_body_changed(target, value, oldvalue, initiator):
        allow_tags=['a','abbr','acronym','b','blockquote','code', 'em',
                'i','li','ol','pre','strong','ul', 'h1','h2','h3','p','img']
        #  转换markdown为html, 并清洗html标签
        if value is None or (value is ''):
            target.body_html = ''
        else:
            target.body_html=bleach.linkify(bleach.clean(
                markdown(value,output_form='html'),
                tags=allow_tags,strip=True,
                attributes={
                    '*': ['class'],
                    'a': ['href', 'rel'],
                    'img': ['src', 'alt'],#支持<img src …>标签和属性
                    }
                ))

    @staticmethod
    def getdate(self):
       data = db.session.query(extract('month', self.create_time).label('month')).first()
       return data[0]


db.event.listen(Pushpost.body, 'set', Pushpost.on_body_changed)# 当body被修改时触发



