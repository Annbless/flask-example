from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, \
        BooleanField,SelectField
from wtforms.validators import Required, EqualTo


class SearchForm(FlaskForm):
    """搜索表单?"""
    searchtype = SelectField('类型', validators=[Required()], choices=[('0','类型'),('1', '编号'), ('2', '名称'), ('3', '作者')])
    search = StringField('书籍编号')
    status = BooleanField('可借')
    submit = SubmitField('搜索')


class BuyForm(FlaskForm):
    id = StringField('编号')
    name = StringField('书名')
    author = StringField('作者')
    storage = IntegerField('库存')
    submit = SubmitField('提交')


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[Required()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('登录')


class queryForm(FlaskForm):
    searchtype = SelectField('检索内容',
                             choices=[('0','检索内容'),('1','馆藏书目查询'),('2','借阅情况查询')])
    submit = SubmitField('检索')



