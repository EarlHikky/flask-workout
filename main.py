from flask import Flask, render_template, url_for, request, flash, session, redirect, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
menu = [{"name": "Новая тренировка", "url": "new-workout"},
        {"name": "Список тренировок", "url": "workouts"},
        {"name": "Добавить упражнение", "url": "add-exercise"}]


@app.route('/')
def index():
    return render_template('base.html', title='Главная', menu=menu)


# @app.route("/profile/<int:username>/<path>")
# def user(username, path):
#     return f'Пользователь: {username} {path}'
@app.route('/user/<username>')
def user(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Пользователь: {username}'


@app.route('/add-exercise', methods=['POST', 'GET'])
def add_exercise():
    if request.method == 'POST':
        print(request.form['title'])
        if len(request.form['title']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('add_exercise.html', title='Добавить упражнение', menu=menu)


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == "selfedu" and request.form['psw'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('user', username=session['userLogged']))

    return render_template('login.html', title="Авторизация", menu=menu)


@app.errorhandler(401)
def pageNotFount(error):
    return render_template('page401.html', title="Доступ запрещён", menu=menu), 401


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404


def test_request():
    with app.test_request_context():
        print(url_for('index'))
        print(url_for('about'))
        print(url_for('user', username="selfedu"))


if __name__ == '__main__':
    app.run(debug=True)
