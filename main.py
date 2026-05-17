from flask import Flask, redirect, url_for, render_template, request, make_response, flash
from sqlite3 import connect

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ_123'


@app.route('/')
def index():
    c = connect('users.db')
    cu = c.cursor()
    cookies = request.cookies.get('id', type=int)

    if cookies is None:
        username = 'Гость'
    else:
        user = cu.execute("SELECT username FROM users WHERE id = ?", (cookies,)).fetchone()
        if user:
            username = user[0]
        else:
            username = 'Гость'
    c.close()
    return render_template('index.html', username=username)


@app.route('/go-to-about', methods=['POST'])
def go_to_about():
    return redirect(url_for('about'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blank')
def blank():
    return render_template('blank.html')


@app.route('/login', methods=['POST'])
def login():
    mail = request.form.get('mail')
    password = request.form.get('password')

    c = connect('users.db')
    cu = c.cursor()

    result = cu.execute("SELECT id FROM users WHERE mail = ? AND password = ?", (mail, password)).fetchone()
    c.close()

    if result:
        id1 = result[0]
        r = make_response(redirect(url_for('index')))
        r.set_cookie('id', str(id1), max_age=60 * 60 * 24 * 7)
        flash('Вход выполнен успешно!', 'success')
        return r
    else:
        flash('Неверный email или пароль', 'error')
        return redirect(url_for('about'))


@app.route('/reg', methods=['POST'])
def reg():
    username = request.form.get('username')
    mail = request.form.get('mail')
    password = request.form.get('pass1')
    password2 = request.form.get('pass2')

    if password != password2:
        flash('Пароли не совпадают', 'error')
        return redirect(url_for('blank'))

    c = connect('users.db')
    cu = c.cursor()

    existing = cu.execute("SELECT id FROM users WHERE mail = ?", (mail,)).fetchone()
    if existing:
        flash('Пользователь с таким email уже существует', 'error')
        c.close()
        return redirect(url_for('blank'))

    existing_name = cu.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing_name:
        flash('Пользователь с таким именем уже существует', 'error')
        c.close()
        return redirect(url_for('blank'))

    id_result = cu.execute("SELECT MAX(id) FROM users").fetchone()[0]
    if id_result is None:
        new_id = 1
    else:
        new_id = id_result + 1

    # Добавляем пользователя
    cu.execute("INSERT INTO users (id, username, mail, password) VALUES (?, ?, ?, ?)",
               (new_id, username, mail, password))
    c.commit()
    c.close()

    flash('Регистрация прошла успешно! Теперь вы можете войти', 'success')
    return redirect(url_for('about'))


@app.route('/logout')
def logout():
    r = make_response(redirect(url_for('index')))
    r.set_cookie('id', '', expires=0)
    flash('Вы вышли из аккаунта', 'info')
    return r


if __name__ == '__main__':
    app.run(debug=True)