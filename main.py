import time
import datetime
from pprint import pp

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from db import User, Exercise, Workout, Sets, WorkoutType

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
# app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/workouts'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# db.init_app(app)
# db.create_all()
menu = [{'name': 'Новая тренировка', 'url': 'add_workout'},
        {'name': 'Список тренировок', 'url': 'show_workouts'},
        {'name': 'Добавить упражнение', 'url': 'add_exercise'},
        {'name': 'Добавить сет', 'url': 'add_set'},
        ]


# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
#     name = db.Column(db.String(50))


# @app.route('/users')
# def users():
#     users = db.session.execute(db.select(User).order_by(User.name)).scalars()
#     print(*(u.name for u in users))
#     return f'Пользователь: {users}'


@app.route('/')
def index():
    return redirect(url_for('show_workouts'))
    # return render_template('base.html', title='Главная', menu=menu)


# @app.route('/profile/<int:username>/<path>')
# def user(username, path):
#     return f'Пользователь: {username} {path}'

# @app.route('/user/<username>')
# def user(username: str):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#     return f'Пользователь: {username}'


# @app.route('/user/<int:user_id>')
# def show_user(user_id: int):
#     user: User = db.get_or_404(User, user_id)
#     return f'Пользователь: {user.name}'
#     # return render_template('user/detail.html', user=user)


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user: User = User(
            name=request.form['name'],
        )
        db.session.add(user)
        db.session.commit()
        # return redirect(url_for('user_detail', user_id=user.id))
        return redirect(url_for('add_workout'))

    return render_template('user/add_user.html', title='Добавить пользователя', menu=menu)


@app.route('/add-exercise', methods=['POST', 'GET'])
def add_exercise():
    types = db.session.execute(db.select(WorkoutType).order_by(WorkoutType.type)).scalars()
    if request.method == 'POST':
        exercise = Exercise(title=request.form['title'], workout_type_id=request.form['type'])
        db.session.add(exercise)
        if not db.session.commit():
            flash('Упражнение добавлено', category='success')
        else:
            flash('Ошибка добавления', category='error')

    return render_template('exercise/add_exercise.html', title='Добавить упражнение', menu=menu, types=types)


@app.route('/add-workout', methods=['POST', 'GET'])
def add_workout():
    types = db.session.execute(db.select(WorkoutType).order_by(WorkoutType.type)).scalars()
    if request.method == 'POST':
        workout = Workout(user_id=1, workout_type_id=request.form['type'])
        db.session.add(workout)
        if not db.session.commit():
            flash('Тренировка добавлена', category='success')
            return redirect(url_for('add_set'))
        else:
            flash('Ошибка добавления', category='error')

    return render_template('workout/add_workout.html', title='Добавить тренировку', menu=menu, types=types)


@app.route('/add-set', methods=['POST', 'GET'])
def add_set():
    current_workout = db.session.execute(db.select(Workout).order_by(desc(Workout.date))).first()[0]
    current_workout_type_id = current_workout.workout_type_id
    # current_workout_type_id = 1
    exercises = db.session.query(Exercise).join(WorkoutType, Exercise.workout_type_id == current_workout_type_id).order_by(WorkoutType.type, Exercise.title).all()
    if request.method == 'POST':
        workout_id = current_workout.id
        set = Sets(
            reps=request.form['reps'] if request.form['reps'] else 0,
            weight=request.form['weight'] if request.form['weight'] else 0,
            workout_id=workout_id,
            exercise_id=request.form['exercise'],
            duration=datetime.timedelta(seconds=int(request.form['duration']) if request.form['duration'] else 0),
            rest=datetime.timedelta(seconds=int(request.form['rest']) if request.form['rest'] else 0),
        )
        db.session.add(set)
        if not db.session.commit():
            flash('Сет добавлен', category='success')
        else:
            flash('Ошибка добавления', category='error')
    return render_template('set/add_set.html', title='Добавить сет', menu=menu, exercises=exercises)


@app.route('/exercises')
def show_exercises():
    exercises = db.session.execute(db.select(Exercise).order_by(Exercise.title)).scalars()
    return render_template('exercise/exercises.html', exercises=exercises, title='Список упражнений', menu=menu)


@app.route('/workout/<workout_id>')
def show_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    return render_template('workout/workout.html', workout=workout,
                           title=f'Тренировка от {workout.date.strftime("%d.%m.%Y")}',
                           menu=menu)


@app.route('/workouts')
def show_workouts():
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
    # app.run(debug=True)
    app.run(debug=True, host='192.168.31.5', port=5000)
    # app.run()
