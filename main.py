from flask import Flask, redirect, url_for, render_template, request, make_response
from sqlite3 import connect

from sympy.codegen.ast import none
from sympy.core import parameters

app = Flask(__name__)


@app.route('/')
def index(*args):
    c = connect('users.db')
    cu = c.cursor()
    cookies = request.cookies.get('id', type=int)
    if cookies is None:
        username = 'Гость'
    else:
        username = cu.execute(f"SELECT username FROM users where id = {cookies}").fetchone()
        if username:
            username = username[0]
        else:
            username = 'Гость'
    c.close()
    return render_template('index.html', username=username)


@app.route('/go-to-about', methods=['POST'])
def go_to_about(*args):
    return redirect(url_for('about'))


@app.route('/about')
def about(*args):
    return render_template('about.html')


@app.route('/blank')
def blank(*args):
    return render_template('blank.html')


@app.route('/login', methods=['POST'])
def login(*args):
    c = connect('users.db')
    cu = c.cursor()
    id1 = cu.execute('SELECT id FROM users WHERE mail = ? and password = ?',
                     (request.form.get('mail'), request.form.get('password'))).fetchone()[0]
    c.close()
    r = make_response(redirect(url_for('index')))
    r.set_cookie('id', str(id1), max_age=60 * 60 * 24 * 7)
    return r


@app.route('/reg', methods=['POST'])
def reg(*args):
    c = connect('users.db')
    cu = c.cursor()
    username = request.form.get('username')
    mail = request.form.get('mail')
    password = request.form.get('pass1')
    id1 = (cu.execute("select max(id) from users").fetchone()[0])
    if id1 is None:
        id1 = 1
    else:
        id1 += 1
    cu.execute("INSERT INTO users (id, username, mail, password) VALUES (?, ?, ?, ?)",
               (id1, username, mail, password))
    c.commit()
    c.close()
    return redirect(url_for('about'))


if __name__ == '__main__':
    app.run()
