import datetime
from collections import defaultdict
from itertools import groupby
from operator import attrgetter

from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from icecream import ic

from db import User, Exercise, Workout, Set, WorkoutType

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/workouts'
# app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# db.init_app(app)
# db.create_all()
menu = [
    {'name': 'Тренировки', 'url': 'show_workouts'},
    {'name': 'Добавить сет', 'url': 'add_set'},
    {'name': 'Упражнения', 'url': 'show_exercises'},
    # {'name': 'Добавить упражнение', 'url': 'add_exercise'},
]


# main = Blueprint('main', __name__) # TODO


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
    return redirect(url_for('add_workout'))


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


@app.route('/stop-set', methods=['POST'])
def stop_set():
    if request.method == 'POST':
        current_set = db.session.query(Set).order_by(desc(Set.id)).first()
        current_set.stop = datetime.datetime.now().replace(microsecond=0)
        current_workout = db.session.query(Workout).order_by(desc(Workout.date)).first()
        # last_set = current_workout.sets[-2] if current_workout.sets else None
        current_set.rest = datetime.timedelta(seconds=int(request.form['rest']))
        # current_set.rest = last_set.stop - current_set.start
        current_set.duration = current_set.stop - current_set.start
        current_set.reps = request.form['reps'] if request.form['reps'] else 0
        current_set.weight = request.form['weight'] if request.form['weight'] else 0

        if db.session.commit():
            flash('Ошибка добавления', category='error')
        flash('Завершение сета', category='success')
        return redirect(url_for('add_set'))
    # return render_template('set/stop_set.html', title='Добавить сет', menu=menu)


@app.route('/add-set', methods=['GET', 'POST'])
def add_set():
    # current_workout = db.session.execute(db.select(Workout).order_by(desc(Workout.date))).scalar()
    current_workout = db.session.execute(
        db.select(Workout).options(joinedload(Workout.sets)).order_by(desc(Workout.date))).scalar()

    if current_workout.stop:
        return redirect(url_for('add_workout'))

    current_workout_id = current_workout.id
    current_workout_type_id = current_workout.workout_type_id

    last_workout = db.session.query(Workout).options(joinedload(Workout.sets).joinedload(Set.exercise)).filter(
        Workout.workout_type_id == current_workout_type_id).order_by(desc(Workout.date)).limit(2).all()[-1]

    last_set_exercise_title = ''
    if len(current_workout.sets) > 0:
        last_set = db.session.query(Set).order_by(desc(Set.id)).first()
        if last_set:
            last_set_exercise_title = last_set.exercise.title

    last_workout_sets_data = {}
    if last_workout:
        last_workout_sets = list(last_workout.sets)
        last_workout_sets.sort(key=lambda s: s.start)
        sorted_sets = sorted(last_workout_sets, key=lambda s: s.exercise.title)
        grouped_sets = groupby(sorted_sets, key=lambda s: s.exercise.title)

        for exercise_title, sets_group in grouped_sets:
            last_workout_sets_data[exercise_title] = {}

            for set_item in sets_group:
                set_index = set_item.index
                set_info = {
                    'weight': set_item.weight,
                    'reps': set_item.reps,
                    'duration': set_item.duration.strftime('%M:%S') if set_item.duration else '0:00',
                    'rest': set_item.rest.strftime('%M:%S') if set_item.rest else '0:00',
                }

                last_workout_sets_data[exercise_title][f'set_{set_index}'] = set_info
    ic(last_workout_sets_data)
    current_exercise_id = None
    exercises = cache.get('exercises')
    if not exercises:
        exercises = (
            db.session.query(Exercise)
            .join(WorkoutType, Exercise.workout_type_id == current_workout_type_id)
            .order_by(WorkoutType.type, Exercise.title)
            .all()
        )
        cache.set('exercises', exercises, timeout=60 * 60)

    current_set_index = 1
    if request.method == 'POST':
        current_exercise_id = int(request.form['exercise'])

        if current_workout.sets:
            filtered_sets = [s for s in current_workout.sets if s.exercise_id == current_exercise_id]
            last_set_index = max(filtered_sets, key=lambda s: s.index) if filtered_sets else None

            if last_set_index:
                current_set_index = last_set_index.index + 1

        new_set = Set(
            index=current_set_index,
            workout_id=current_workout_id,
            exercise_id=current_exercise_id,
            start=datetime.datetime.now().replace(microsecond=0)
        )

        db.session.add(new_set)
        db.session.commit()
        if not db.session.commit():
            flash('Сет добавлен', category='success')
            # return redirect(url_for('add_set'))
        else:
            flash('Ошибка добавления', category='error')

    return render_template('set/add_set.html', title='Добавить сет', menu=menu, exercises=exercises,
                           current_set_index=current_set_index, current_exercise_id=current_exercise_id,
                           last_set_exercise_title=last_set_exercise_title,
                           last_workout_sets_data=last_workout_sets_data)


@app.route('/update_set/<int:set_id>', methods=['GET', 'POST'])
def update_set(set_id):
    set_info = db.get_or_404(Set, set_id)
    if request.method == 'POST':
        set_info.index = request.form['serial'],
        set_info.index = request.form['index'],
        set_info.reps = request.form['reps'],
        set_info.weight = request.form['weight'],
        set_info.start = request.form['start'],
        set_info.stop = request.form['stop'],
        set_info.duration = request.form['duration'],
        set_info.rest = request.form['rest']
        db.session.commit()
        return render_template('set/update_set.html', set_info=set_info, menu=menu)
    else:
        return render_template('set/update_set.html', set_info=set_info, menu=menu)


@app.route('/set/<set_id>/delete', methods=['POST'])
def delete_set(set_id):
    set_info = db.get_or_404(Set, set_id)
    db.session.delete(set_info)
    db.session.commit()
    return redirect(url_for('show_workouts'))


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


@app.route('/exercises')
def show_exercises():
    exercises = db.session.execute(db.select(Exercise).order_by(Exercise.title)).scalars()
    return render_template('exercise/exercises.html', exercises=exercises, title='Упражнения', menu=menu)


@app.route('/exercise/<exercise_id>', methods=['GET', 'POST'])
def update_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    if request.method == 'POST':
        exercise.title = request.form['title']
        exercise.workout_type_id = request.form['workout_type_id']
        db.session.commit()
        return redirect(url_for('show_exercises'))

    else:
        workout_types = db.session.execute(db.select(WorkoutType).order_by(WorkoutType.type)).scalars()
        return render_template('exercise/update_exercise.html', exercise=exercise, workout_types=workout_types,
                               menu=menu)


@app.route('/exercise/<exercise_id>/delete', methods=['POST'])
def delete_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return redirect(url_for('show_exercises'))


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

    return render_template('workout/add_workout.html', title='Тренировка', menu=menu, types=types)


@app.route('/workout/<workout_id>')
def show_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    return render_template('workout/workout.html', workout=workout,
                           title=f'Тренировка от {workout.date.strftime("%d.%m.%Y")}',
                           menu=menu)


@app.route('/workout-stop', methods=['POST'])
def stop_workout():
    current_workout = db.session.execute(db.select(Workout).order_by(desc(Workout.date))).first()[0]
    current_workout.stop = datetime.datetime.now().replace(microsecond=0)
    current_workout.duration = current_workout.stop - current_workout.date
    db.session.commit()
    return redirect(url_for('show_workouts'))


@app.route('/workouts')
def show_workouts():
    workouts = db.session.execute(db.select(Workout).order_by(Workout.date)).scalars()
    return render_template('workout/workouts.html', workouts=workouts, title='Список тренировок', menu=menu)


@app.route('/delete-workout/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout:
        db.session.query(Set).filter(Set.workout_id == workout_id).delete()
        db.session.delete(workout)
        if not db.session.commit():
            flash('Тренировка удалена', category='success')
        else:
            flash('Тренировка не удалена', category='error')
    else:
        flash('Тренировка не найдена', category='error')

    return redirect(url_for('show_workouts'))


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if 'userLogged' in session:
#         return redirect(url_for('user', username=session['userLogged']))
#     elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
#         session['userLogged'] = request.form['username']
#         return redirect(url_for('user', username=session['userLogged']))
#
#     return render_template('login.html', title='Авторизация', menu=menu)


@app.errorhandler(401)
def access_denied(error):
    return render_template('page401.html', title='Доступ запрещён', menu=menu), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


# @app.route('/test', methods=['POST', 'GET'])
# def test():
#     current_workout = db.session.execute(db.select(Workout).order_by(desc(Workout.date))).first()[0]
#     current_workout_type_id = current_workout.workout_type_id
#     # current_workout_type_id = 1
#     exercises = db.session.query(Exercise).join(WorkoutType,
#                                                 Exercise.workout_type_id == current_workout_type_id).order_by(
#         WorkoutType.type, Exercise.title).all()
#     if request.method == 'POST':
#         workout_id = current_workout.id
#         set = Set(
#             reps=request.form['reps'] if request.form['reps'] else 0,
#             weight=request.form['weight'] if request.form['weight'] else 0,
#             workout_id=workout_id,
#             exercise_id=request.form['exercise'],
#             # duration=datetime.timedelta(seconds=int(request.form['duration']) if request.form['duration'] else 0),
#             rest=datetime.timedelta(seconds=int(request.form['rest']) if request.form['rest'] else 0),
#         )
#         # current_workout.duration = current_workout.duration + datetime.datetime.now()
#         # db.session.add(set)
#         # if not db.session.commit():
#         #     flash('Сет добавлен', category='success')
#         # else:
#         #     flash('Ошибка добавления', category='error')
#         print(request.form['rest'])
#     return render_template('test.html', title='Добавить сет', menu=menu, exercises=exercises)


def test_request():
    with app.test_request_context():
        print(url_for('index'))
        print(url_for('about'))
        print(url_for('user', username='selfedu'))


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='192.168.31.5', port=5000)
    # app.run(host='192.168.31.5', port=5000)
    # app.run()
