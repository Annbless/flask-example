from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


"""
# python 3搜索的不兼容
if sys.version_info[0] == 3:
    enable_search = False
else:
    enable_search = True
    import flask.ext.whooshalchemy as whooshalchemy
"""

Base = declarative_base()

class Book(Base):
    __tablename__ = 'Book'

    id = Column(String(20),primary_key=True)
    name = Column(String(30))
    author = Column(String(20))
    storage = Column(Integer)
    borrow = Column(Integer)

class User( Base , UserMixin):
    __tablename__ = 'user'

    id = Column(String(20),primary_key=True)
    password = Column(String(20))
    status = Column(Integer)

engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/Bookdata')
DBsession = sessionmaker(bind = engine)

'''

class Book(db.Model):
    """图书类"""
    __searchable__ = ['name', 'tag', 'summary']
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(164))
    name = db.Column(db.Text)
    author = db.Column(db.Text)
    tag = db.Column(db.String(164))
    summary = db.Column(db.Text)
    image = db.Column(db.String(164))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Boolean)
    start = db.Column(db.String(164))
    end = db.Column(db.String(164))

    def __repr__(self):
        return "%r :The instance of class Book" % self.name
'''

'''
class User(db.Model, UserMixin):
    """用户类"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(164))
    password_hash = db.Column(db.String(164))
    book = db.relationship('Book', backref="user", lazy="dynamic")

    @login_manager.user_loader
    def load_user(user_id):
        """flask-login要求实现的用户加载回调函数
           依据用户的unicode字符串的id加载用户"""
        return User.query.get(int(user_id))

    @property
    def password(self):
        """将密码方法设为User类的属性"""
        raise AttributeError('无法读取密码原始值!')

    @password.setter
    def password(self, password):
        """设置密码散列值"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码散列值"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "%r :The instance of class User" % self.username
        





if enable_search:
    whooshalchemy.whoosh_index(app, Book)
'''

