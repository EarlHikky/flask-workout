from pprint import pp

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort
from flask_sqlalchemy import SQLAlchemy

from db import User, Exercise, Workout

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
# app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/workouts'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# db.init_app(app)
# db.create_all()
menu = [{'name': 'Новая тренировка', 'url': 'new-workout'},
        {'name': 'Список тренировок', 'url': 'workouts'},
        {'name': 'Добавить упражнение', 'url': 'add-exercise'}]


# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
#     name = db.Column(db.String(50))


@app.route('/users')
def users():
    users = db.session.execute(db.select(User).order_by(User.name)).scalars()
    print(*(u.name for u in users))
    return f'Пользователь: {users}'


@app.route('/')
def index():
    return render_template('base.html', title='Главная', menu=menu)


# @app.route('/profile/<int:username>/<path>')
# def user(username, path):
#     return f'Пользователь: {username} {path}'

@app.route('/user/<username>')
def user(username: str):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Пользователь: {username}'


@app.route('/user/<int:user_id>')
def user_detail(user_id: int):
    user: User = db.get_or_404(User, user_id)
    return f'Пользователь: {user.name}'
    # return render_template('user/detail.html', user=user)


@app.route('/users/create', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        user: User = User(
            name=request.form['name'],
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user.id))

    return render_template('user/create.html', title='Добавить пользователя', menu=menu)


@app.route('/add-exercise', methods=['POST', 'GET'])
def add_exercise():
    if request.method == 'POST':
        exercise = Exercise(title=request.form['title'])
        db.session.add(exercise)
        if not db.session.commit():
            flash('Упражнение добавлено', category='success')
        else:
            flash('Ошибка добавления', category='error')

    return render_template('exercise/add_exercise.html', title='Добавить упражнение', menu=menu)


@app.route('/exercises')
def exercises():
    exercises = db.session.execute(db.select(Exercise).order_by(Exercise.title)).scalars()
    return render_template('exercise/exercises.html', exercises=exercises, title='Список упражнений', menu=menu)


@app.route('/workouts')
def workouts():
    workouts = db.session.execute(db.select(Workout).order_by(Workout.date)).scalars()
    return render_template('workout/workouts.html', workouts=workouts, title='Список тренировок', menu=menu)



@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('user', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('user', username=session['userLogged']))

    return render_template('login.html', title='Авторизация', menu=menu)


@app.errorhandler(401)
def access_denied(error):
    return render_template('page401.html', title='Доступ запрещён', menu=menu), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


def test_request():
    with app.test_request_context():
        print(url_for('index'))
        print(url_for('about'))
        print(url_for('user', username='selfedu'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
