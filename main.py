from flask import Flask,request
from flask import render_template
from flask import flash
from flask import redirect
from flask_login import LoginManager,login_user,logout_user,login_required
from forms import SearchForm,BuyForm,LoginForm,queryForm
from flask_bootstrap import Bootstrap
from flask_login import current_user
import urllib.request
import json
import mysql.connector

app = Flask(__name__)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '123456'
app.config['MAX_SEARCH_RESULTS'] = 5
login_manager.login_view = 'login'
login_manager.login_message = "Please sign in"


@login_manager.user_loader
def user_loader(id):
    from models import User
    conn = mysql.connector.connect(user='root', password='', database='Bookdata')
    cursor = conn.cursor()
    cursor.execute('select * from user where id = %s', (id,))
    results = cursor.fetchall()
    cursor.close()
    user = User()
    user.id = results[0][0]
    user.password = results[0][1]
    user.status = results[0][2]
    return user


@app.route('/login/',methods=["POST","GET"])
def login():
    from models import User
    form = LoginForm()
    if form.validate_on_submit():
        userid = form.username.data
        userpassword = form.password.data
        conn = mysql.connector.connect(user='root', password='', database='Bookdata')
        cursor = conn.cursor()
        cursor.execute('select * from user where id = %s',(userid,))
        results = cursor.fetchall()
        cursor.close()
        if results == []:
            flash('wrong')
            return render_template('show.html',mess = userpassword)
        elif userpassword != results[0][1]:
            flash('wrong password')
        else:
            user = User()
            user.id = userid
            user.password = userpassword
            user.status = results[0][2]
            login_user(user,remember=True)
            return redirect('/index/')
    return render_template('login.html',form = form)

@app.route('/index/',methods=["POST","GET"])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        bookid = form.search.data
        searchtype = form.searchtype.data
        if form.status.data:
            status = 'true'
            return redirect('/search/'+bookid + '/' + status + '/' + searchtype)
        else:
            status = 'false'
            return redirect('/search/' + bookid + '/' + status + '/' + searchtype)
    return render_template('try.html',form = form)


@app.route('/search/<bookid>/<status>/<searchtype>',methods=["POST","GET"])
def search(bookid,status,searchtype):
    # to connect the database
    conn = mysql.connector.connect(user = 'root',password = '',database='Bookdata')
    cursor = conn.cursor()
    if status == 'true' and searchtype == '1':
        cursor.execute("select * from Book where id like %s and storage > 0", ('%' + bookid + '%',))
    elif status == 'false' and searchtype == '1':
        cursor.execute("select * from Book where id like %s", ('%' + bookid + '%',))
    elif status == 'false' and searchtype == '2':
        cursor.execute("select * from Book where name like %s", ('%' + bookid + '%',))
    elif status == 'true' and searchtype == '2':
        cursor.execute("select * from Book where name like %s and storage > 0", ('%' + bookid + '%',))
    elif status == 'true' and searchtype == '3':
        cursor.execute("select * from Book where author like %s and storage > 0", ('%' + bookid + '%',))
    else:
        cursor.execute("select * from Book where author like %s", ('%' + bookid + '%',))
    results = cursor.fetchall()
    cursor.close()
    if results == []:
        flash("No such book here")
        return redirect('/index')
    return render_template('queryresult.html',booklist = results)


@app.route('/buyresult/<bookid>',methods=["POST","GET"])
def buyresult(bookid):
    # to connect the database
    conn = mysql.connector.connect(user = 'root',password = '',database='Bookdata')
    cursor = conn.cursor()
    cursor.execute("select * from Book where id like %s and storage > 0", (bookid,))
    results = cursor.fetchall()
    cursor.close()
    return render_template('queryresult.html',booklist = results)


@app.route('/borrow/<bookid>',methods=["POST","GET"])
@login_required
def borrow(bookid):
    conn = mysql.connector.connect(user='root', password='', database='Bookdata')
    cursor = conn.cursor()
    cursor.execute('select * from borrow where userid = %s and bookid = %s',(current_user.id,bookid,))
    results = cursor.fetchall()
    if results == []:
        cursor.execute("select count(*) from borrow where userid = %s group by userid",(current_user.id,))
        count = cursor.fetchall()
        if count == [] or count[0][0] < 7:
            cursor.execute('update book set storage = storage - 1, borrow = borrow + 1 where id = %s', (bookid,))
            conn.commit()
            cursor.execute('insert into borrow values (%s,%s)',(bookid, current_user.id,))
            conn.commit()
            cursor.close()
            return redirect('/borrowed/')
        else:
            cursor.close()
            return render_template('error.html', mess="已经到达借阅上限")
    else:
        cursor.close()
        return render_template('error.html',mess = "已经借阅过该书")


@app.route('/borrowed/')
@login_required
def borrowed():
    conn = mysql.connector.connect(user='root', password='', database='Bookdata')
    cursor = conn.cursor()
    cursor.execute('select book.id,book.name,book.author from book,borrow where book.id = borrow.bookid and userid = %s',(current_user.id,))
    results = cursor.fetchall()
    cursor.close()
    if results == []:
        return redirect('/index')
    return render_template('borrowed.html',booklist = results)


@app.route('/query/',methods=["POST","GET"])
@login_required
def query():
    form = queryForm()
    if form.validate_on_submit():
        searchtype = form.searchtype.data
        conn = mysql.connector.connect(user='root', password='', database='Bookdata')
        cursor = conn.cursor()
        if searchtype == '1':
            cursor.execute('select * from Book')
            results = cursor.fetchall()
            cursor.close()
            return render_template('queryinit1.html', form=form, list=results, type = searchtype)

        else:
            cursor.execute('select book.id,book.name,borrow.userid from Borrow,Book where borrow.bookid = book.id group by borrow.userid')
            results = cursor.fetchall()
            cursor.close()
            return render_template('queryinit.html', form=form, list=results, type = searchtype)

    return render_template('queryinit.html',form = form, list = [], type = 0)


@app.route('/reload/<bookid>')
@login_required
def reload(bookid):
    conn = mysql.connector.connect(user='root', password='', database='Bookdata')
    cursor = conn.cursor()
    cursor.execute('update book set storage = storage + 1, borrow = borrow - 1 where id = %s', (bookid,))
    conn.commit()
    cursor.execute('delete from borrow where bookid = %s and userid = %s', (bookid, current_user.id,))
    conn.commit()
    cursor.close()
    return redirect('/borrowed/')


@app.route('/buy/',methods=["POST","GET"])
@login_required
def buy():
    form = BuyForm()
    if form.validate_on_submit():
        bookid = form.id.data
        bookname = form.name.data
        bookauthor = form.author.data
        bookstorage = form.storage.data
        conn = mysql.connector.connect(user='root', password='', database='Bookdata')
        cursor = conn.cursor()
        cursor.execute("insert into Book (id,name,author,storage,borrow) values (%s,%s,%s,%s,0)",
                       (bookid, bookname, bookauthor, bookstorage,))
        conn.commit()
        cursor.close()
        return redirect('/buyresult/'+bookid)
    return render_template('buy.html',form = form)


@app.route('/info/<bookname>',methods=["POST","GET"])
def info(bookname):
    get_url = "https://api.douban.com/v2/book/search?q=%s" % bookname
    resp_1 = json.loads(urllib.request.urlopen(get_url).read())
    book_id = resp_1['books'][0]['id']
    url = "https://api.douban.com/v2/book/%s" % book_id
    resp_2 = json.loads(urllib.request.urlopen(url).read())
    summary = resp_2['summary']
    image = resp_2['images'].get('large')
    s = 'https://images.weserv.nl/?url='
    for i in range(len(image) - 8):
        """
                if image[i + 8] == '/':
            s += '//'
        else:
            s += image[i + 8]
        """
        s += image[i + 8]
    return render_template('info.html',image = s,name = bookname,summary = summary)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/index')

if __name__ == '__main__':
    app.run()
