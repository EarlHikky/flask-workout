import datetime
import time

from itertools import groupby
from typing import Tuple

from flask import Flask, render_template, url_for, request, flash, redirect, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_caching import Cache
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from icecream import ic
from werkzeug import Response

from db import User, Exercise, Workout, Set, WorkoutType, Target
from user import UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/earl/PycharmProjects/flask-workout/database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/workouts'
# app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# engine = create_engine('sqlite:////home/earl/PycharmProjects/flask-workout/database.db')
db = SQLAlchemy(app)
# db.init_app(app)
# db.create_all()

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'info'

menu = [
    {'name': 'Тренировки', 'url': 'show_workouts'},
    {'name': 'Старт', 'url': 'start_set'},
    {'name': 'Упражнения', 'url': 'show_exercises'},
]


# main = Blueprint('main', __name__) # TODO


@login_manager.user_loader
def load_user(user_id: int) -> UserLogin:
    return UserLogin(user_id)


@app.route('/login', methods=['POST', 'GET'])
def login() -> Response | str:
    if request.method == 'POST':
        username = request.form['username']
        user = db.session.execute(db.select(User).filter_by(name=username)).scalar()

        if user is None:
            # If the user doesn't exist, create a new one
            new_user = User(name=username)
            db.session.add(new_user)
            if not db.session.commit():
                # If the user is created, log in
                user_login = UserLogin(new_user.id)
                login_user(user_login, remember=True)

                flash('Создание нового пользователя', 'success')
                return redirect(url_for('index'))

            else:
                flash('Что-то пошло не так', 'error')
                return redirect(url_for('login'))

        else:
            # If the user exists, log in
            user_login = UserLogin(user.id)
            remember = True if request.form.get('remember') else False
            login_user(user_login, remember=remember)

            flash('Успешный вход', 'info')
            return redirect(url_for('index'))

    return render_template('login.html', title='Авторизация')


@app.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


def is_new_workout() -> Workout | None:
    """
    Check if there is a new workout.

    :return: Workout object or None.
    """
    user_id = current_user.id
    workout = db.session.execute(
        db.select(Workout).filter(Workout.user_id == user_id).order_by(desc(Workout.date))).scalar()
    if workout and not workout.stop:
        return workout


def get_context(workout: Workout, w_type: str = None) -> dict:
    """
    Get context for template.

    :param workout:
    :param w_type:
    :return:
    """
    workout_id = workout.id
    workout_type_id = workout.workout_type_id
    exercises = cache.get('exercises')
    if not exercises:
        exercises = (
            db.session.query(Exercise)
            .join(WorkoutType, Exercise.workout_type_id == workout_type_id).filter(
                Exercise.user_id == current_user.id)
            .order_by(WorkoutType.type, Exercise.title)
            .all()
        )
        cache.set('exercises', exercises, timeout=60 * 60)

    for item in menu:
        if item['name'] == 'Старт':
            item['name'] = 'Прод..'
            if w_type == 'new':
                item['url'] = 'start_new_set'
            else:
                item['url'] = 'start_set'

    context = {
        'menu': menu,
        'exercises': exercises,
        'current_workout_id': workout_id,
    }
    return context


# @app.route('/register', methods=['POST', 'GET'])
# def register():
#     if request.method == 'POST':
#         user = User(name=request.form['username'])
#         db.session.add(user)
#         if not db.session.commit():
#             flash('Пользователь с таким именем уже существует', 'error')
#             return render_template('register.html', title='Регистрация')
#         return redirect(url_for('login'))
#
#     return render_template('register.html', title='Регистрация')


@app.route('/')
@login_required
def index() -> Response:
    return redirect(url_for('add_workout'))


@app.route('/profile')  # TODO
@login_required
def profile() -> str:
    return f'ID пользователя {current_user.id}'


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


# @app.route('/user/add', methods=['GET', 'POST'])
# def add_user():
#     if request.method == 'POST':
#         user: User = User(
#             name=request.form['name'],
#         )
#         db.session.add(user)
#         db.session.commit()
#         # return redirect(url_for('user_detail', user_id=user.id))
#         return redirect(url_for('add_workout'))
#
#     return render_template('user/add_user.html', title='Добавить пользователя', menu=menu)


@app.route('/set/start/new', methods=['GET'])
@login_required
def start_new_set() -> Response | str:
    """
    Start new set without data from last workout.

    :return: Render HTML for start_new_set or Redirect.
    """
    current_workout = is_new_workout()
    if not current_workout:
        return redirect(url_for('add_workout'))

    context = get_context(current_workout, w_type='new')
    current_set_index = 1
    last_set_exercise_title = ''
    if len(current_workout.sets) > 0:
        last_set = db.session.query(Set).order_by(desc(Set.id)).first()
        if last_set:
            last_set_exercise_title = last_set.exercise.title
            last_set_index = last_set.index
            current_set_index = last_set_index + 1
    context['last_set_exercise_title'] = last_set_exercise_title
    context['set_index'] = current_set_index
    context['rest'] = '01:30'
    context['seconds'] = 0
    context['duration'] = 0

    return render_template('set/start_new_set.html', **context)


def is_increasing(lst: list) -> bool:
    """
    Проверяет список на возрастание
    :param lst:
    :return:
    """
    if lst[-1] == lst[-2]:
        return True
    return all(i < j for i, j in zip(lst, lst[1:]))


def growth_rate(lst: list) -> float:
    """
    Рассчитывает коэффициент прогресса
    :param lst:
    :return:
    """
    return (lst[-1] - lst[0]) / (len(lst) - 1)


def convert_dt_to_seconds(rest: datetime) -> int:
    """
    Convert datetime to seconds
    :param rest:
    :return:
    """
    return rest.hour * 3600 + rest.minute * 60 + rest.second


def convert_seconds_to_str(seconds: int) -> str:
    """
    Convert seconds to string
    :param seconds:
    :return:
    """
    tdelta = datetime.timedelta(seconds=seconds)
    parts = str(tdelta).split(':')
    return '{}:{}'.format(parts[1], parts[2])


@app.route('/set/start', methods=['GET'])
@login_required
def start_set() -> Response | str:
    """
    Start new set
    :return: Render template or redirect.
    """
    current_workout = is_new_workout()
    if not current_workout:
        return redirect(url_for('add_workout'))

    context = get_context(current_workout)

    # current_workout_id = current_workout.id
    current_workout_type_id = current_workout.workout_type_id
    current_workout_sets = current_workout.sets
    current_workout_sets.sort(key=lambda x: x.index)

    user_id = current_user.id

    last_workouts = db.session.query(Workout).options(joinedload(Workout.sets).joinedload(Set.exercise)).filter(
        Workout.user_id == user_id).filter(
        Workout.workout_type_id == current_workout_type_id).order_by(desc(Workout.date)).limit(4).all()

    # form = {'target': 'power'}
    # if len(last_workouts) > 2:
    # if len(last_workouts) > 1:

    # if len(last_workouts) > 3:
    # workouts = last_workouts[1:]
    # workouts.sort(key=lambda x: x.date)
    #
    # target = form['target']
    # if target == 'power':
    #     sets = [workout.sets for workout in workouts if workout.sets]
    #
    #     current_set_index = 0
    #     weights = [s.weight for set_ in sets for s in set_ if s.index == current_set_index + 1]
    #
    #     ic(weights)
    #
    #     last_weight = weights[-1]
    #     if is_increasing(weights):
    #         current_weight = round(last_weight + growth_rate(weights), 1)
    #         context['weight'] = current_weight
    # elif target == 'reps':
    #     reps = [20, 21, 25]
    #     last_rep = reps[-1]
    #     if is_increasing(reps):
    #         current_reps = round(last_rep + growth_rate(reps))
    # elif target == 'endurance':
    #     durations = [40, 41, 45]
    #     rests = [90, 89, 85]
    #     last_duration = durations[-1]
    #     last_rest = rests[-1]
    #     if is_increasing(durations):
    #         current_duration = round(last_duration + growth_rate(durations))
    #     if not is_increasing(rests):
    #         current_rest = round(last_rest + growth_rate(rests))

    if len(last_workouts) > 1:
        last_workout = last_workouts[1]
        last_workout_sets = cache.get('last_workout_sets')
        if not last_workout_sets:
            last_workout_sets = last_workout.sets
            last_workout_sets.sort(key=lambda x: x.index)
            cache.set('last_workout_sets', last_workout_sets, timeout=60 * 30)

        if current_workout_sets:
            current_set_index = current_workout_sets[-1].index
        else:
            current_set_index = 0

        if not current_set_index == last_workout_sets[-1].index:
            # context['current_workout_id'] = current_workout_id
            context['current_set_index'] = current_set_index + 1
            context['exercise_title'] = last_workout_sets[current_set_index].exercise.title
            context['exercise_id'] = last_workout_sets[current_set_index].exercise.id
            context['weight'] = last_workout_sets[current_set_index].weight
            context['reps'] = last_workout_sets[current_set_index].reps
            context['duration'] = last_workout_sets[current_set_index].duration.strftime('%M:%S')
            if current_set_index == 0:
                previous_set_rest = last_workout_sets[current_set_index].rest
            else:
                previous_set_rest = last_workout_sets[current_set_index - 1].rest
            seconds = convert_dt_to_seconds(previous_set_rest)
            context['rest'] = previous_set_rest.strftime('%M:%S')
            context['seconds'] = seconds

            if len(last_workouts) > 3:
                workouts = last_workouts[1:]
                workouts.sort(key=lambda x: x.date)
                sets = [workout.sets for workout in workouts if workout.sets]
                target = current_workout.target_id

                if target == 1:  # TODO
                    weights = [s.weight for set_ in sets for s in set_ if s.index == current_set_index + 1]
                    last_weight = weights[-1]
                    if is_increasing(weights):
                        current_weight = round(last_weight + growth_rate(weights), 1)
                        context['weight'] = current_weight
                elif target == 2:
                    reps = [s.reps for set_ in sets for s in set_ if s.index == current_set_index + 1]
                    last_rep = reps[-1]
                    if is_increasing(reps):
                        current_reps = round(last_rep + growth_rate(reps))
                        context['reps'] = current_reps
                elif target == 3:
                    durations = [convert_dt_to_seconds(s.duration) for set_ in sets for s in set_ if
                                 s.index == current_set_index + 1]
                    rests = [convert_dt_to_seconds(s.rest) for set_ in sets for s in set_ if
                             s.index == current_set_index + 1]
                    last_duration = durations[-1]
                    last_rest = rests[-1]
                    if is_increasing(durations):
                        current_duration = round(last_duration + growth_rate(durations))
                        context['duration'] = convert_seconds_to_str(current_duration)
                    if not is_increasing(rests):
                        current_rest = round(last_rest + growth_rate(rests))
                        context['rest'] = convert_seconds_to_str(current_rest)
        else:
            flash('Конец тренировки', category='success')
            return redirect(url_for('stop_workout'))
    else:
        return redirect(url_for('start_new_set'))

    return render_template('set/start_set.html', **context)


@app.route('/set/stop', methods=['POST'])
@login_required
def stop_set() -> Response:
    """
    Stop current set. Set new rest time for last set.

    :return: Render HTML template.
    """
    if request.method == 'POST':
        current_set = db.session.query(Set).order_by(desc(Set.id)).first()
        current_set.stop = datetime.datetime.now().replace(microsecond=0)
        current_workout = db.session.query(Workout).order_by(desc(Workout.date)).first()
        current_workout_sets = current_workout.sets

        if len(current_workout_sets) > 1:
            current_workout_sets.sort(key=lambda x: x.index)
            last_set = current_workout.sets[-2] if current_workout.sets else None
            last_set.rest = current_set.start - last_set.stop

        current_set.duration = current_set.stop - current_set.start
        current_set.reps = request.form['reps'] if request.form['reps'] else 0
        current_set.weight = request.form['weight'] if request.form['weight'] else 0
        current_set.rest = datetime.timedelta(seconds=0)

        if db.session.commit():
            flash('Ошибка добавления', category='error')
        flash('Завершение сета', category='success')
        return redirect(request.referrer or '/workouts')


@app.route('/set/add', methods=['POST'])
@login_required
def add_set() -> Response | str:
    """
    Add new set.

    :return: Redirect to last page.
    """
    ic(request.form['set_index'])
    workout_id = int(request.form['workout_id'])
    set_index = int(request.form['set_index'])

    exercise_id = int(request.form['exercise_id'])
    new_set = Set(
        index=set_index,
        workout_id=workout_id,
        exercise_id=exercise_id,
        start=datetime.datetime.now().replace(microsecond=0)
    )
    db.session.add(new_set)
    if not db.session.commit():
        flash('Сет добавлен', category='success')
    else:
        flash('Ошибка добавления', category='error')
    return redirect(request.referrer or '/workouts')


@app.route('/set/<int:set_id>', methods=['GET', 'POST'])
@login_required
def update_set(set_id: int) -> Response | str:
    """
    Update workout set.

    :param set_id:
    :return: Render template or redirect to show_workout page.
    """
    set_info = db.get_or_404(Set, set_id)
    if request.method == 'POST':
        set_info.index = request.form['index'],
        set_info.reps = request.form['reps'],
        set_info.weight = request.form['weight'],
        set_info.start = request.form['start'],
        set_info.stop = request.form['stop'],
        set_info.duration = request.form['duration'],
        set_info.rest = request.form['rest']
        if not db.session.commit():
            flash('Сет обновлён', category='success')
            return redirect(url_for('show_workout', workout_id=set_info.workout_id))
        else:
            flash('Ошибка обновления', category='error')
    return render_template('set/update_set.html', set_info=set_info, menu=menu)


@app.route('/set/<int:set_id>/delete', methods=['POST'])
@login_required
def delete_set(set_id: int) -> Response | str:
    """
    Delete workout set.

    :param set_id:
    :return: Redirect to show_workout page.
    """
    set_info = db.get_or_404(Set, set_id)
    db.session.delete(set_info)
    if not db.session.commit():
        flash('Сет удалён', category='success')
    else:
        flash('Ошибка удаления', category='error')
    return redirect(url_for('show_workout', workout_id=set_info.workout_id))


@app.route('/exercise/add', methods=['POST', 'GET'])
@login_required
def add_exercise() -> Response | str:
    """
    Add new exercise.

    :return: Rendered template for adding new exercise.
    """
    user_id = current_user.id
    targets = db.session.execute(db.select(Target).order_by(Target.title)).scalars()
    types = db.session.execute(
        db.select(WorkoutType).filter(WorkoutType.user_id == user_id).order_by(WorkoutType.type)).scalars()
    if request.method == 'POST':
        exercise = Exercise(user_id=user_id, title=request.form['title'], workout_type_id=request.form['type'])
        db.session.add(exercise)
        if not db.session.commit():
            flash('Упражнение добавлено', category='success')
            return redirect(url_for('show_exercises'))
        else:
            flash('Ошибка добавления', category='error')
    return render_template('exercise/add_exercise.html', title='Добавить упражнение', menu=menu, types=types,
                           targets=targets)


@app.route('/exercises')
@login_required
def show_exercises() -> str:
    """
    Show all exercises.

    :return: Rendered template for the list of exercises.
    """
    user_id = current_user.id
    exercises = db.session.execute(
        db.select(Exercise)
        .filter(Exercise.user_id == user_id)
        .order_by(Exercise.title)
    ).scalars()
    return render_template('exercise/exercises.html', exercises=exercises, title='Упражнения', menu=menu)


@app.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def update_exercise(exercise_id: int) -> Response | str:
    """
    Update an exercise.

    :param exercise_id:
    :return: Redirect to the list of exercises or HTML template with the updated exercise.
    """
    exercise = db.get_or_404(Exercise, exercise_id)
    if request.method == 'POST':
        exercise.title = request.form['title']
        exercise.workout_type_id = request.form['workout_type_id']
        exercise.target_id = request.form['target']
        db.session.commit()
        return redirect(url_for('show_exercises'))

    else:
        workout_types = db.session.execute(db.select(WorkoutType).order_by(WorkoutType.type)).scalars()
        targets = db.session.execute(db.select(Target).order_by(Target.title)).scalars()
        return render_template('exercise/update_exercise.html', exercise=exercise, workout_types=workout_types,
                               menu=menu, targets=targets)


@app.route('/exercise/<int:exercise_id>/delete', methods=['POST'])
@login_required
def delete_exercise(exercise_id: int) -> Response | str:
    """
    Delete an exercise.

    :param exercise_id:
    :return: Redirect to the list of exercises.
    """
    exercise = db.get_or_404(Exercise, exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return redirect(url_for('show_exercises'))


@app.route('/target/add', methods=['GET', 'POST'])
@login_required
def add_target() -> Response | str:
    """
    Add new target.

    :return:
    """
    if request.method == 'POST':
        user_id = current_user.id
        target = Target(title=request.form['title'], user_id=user_id)
        db.session.add(target)
        if not db.session.commit():
            flash('Цель добавлена', category='success')
            return redirect(url_for('add_exercise'))
        else:
            flash('Ошибка добавления', category='error')
    return render_template('target/add_target.html', title='Добавить цель', menu=menu)


@app.route('/target/<int:target_id>/update', methods=['GET', 'POST'])
@login_required
def update_target(target_id: int) -> Response | str:
    """
    Update target.

    :param target_id:
    :return: Redirect to the list of exercises or HTML template with the updated exercise.
    """
    target = db.get_or_404(Target, target_id)
    if request.method == 'POST':
        target.title = request.form['title']
        db.session.commit()
        return redirect(url_for('add_exercise'))
    else:
        return render_template('target/update_target.html', target=target, menu=menu)


@app.route('/target/<int:target_id>/delete', methods=['POST'])
@login_required
def delete_target(target_id: int) -> Response | str:
    """
    Delete target.

    :param target_id:
    :return: Redirect to the list of exercises.
    """
    target = db.get_or_404(Target, target_id)
    db.session.delete(target)
    db.session.commit()
    return redirect(url_for('add_exercise'))


@app.route('/workout/type/add', methods=['GET', 'POST'])
@login_required
def add_workout_type() -> Response | str:
    """
    Add new workout type.

    :return: Rendered template for adding new workout type.
    """
    if request.method == 'POST':
        user_id = current_user.id
        workout_type = WorkoutType(type=request.form['title'], user_id=user_id)
        db.session.add(workout_type)
        if not db.session.commit():
            flash('Тип добавлен', category='success')
            return redirect(url_for('add_exercise'))
        else:
            flash('Ошибка добавления', category='error')
    return render_template('workout_type/add_workout_type.html', title='Добавить тип', menu=menu)


@app.route('/workout/type/<int:workout_type_id>/update', methods=['GET', 'POST'])
@login_required
def update_workout_type(workout_type_id: int) -> Response | str:
    """
    Update workout type.

    :param workout_type_id:
    :return: Redirect to the list of exercises or HTML template with the updated exercise.
    """
    workout_type = db.get_or_404(WorkoutType, workout_type_id)
    if request.method == 'POST':
        workout_type.type = request.form['title']
        db.session.commit()
        return redirect(url_for('show_exercises'))
    else:
        return render_template('workout_type/update_workout_type.html', workout_type=workout_type, menu=menu)


@app.route('/workout/type/<int:workout_type_id>/delete', methods=['POST'])
@login_required
def delete_workout_type(workout_type_id: int) -> Response | str:
    """
    Delete workout type.

    :param workout_type_id:
    :return: Redirect to the list of exercises.
    """
    workout_type = db.get_or_404(WorkoutType, workout_type_id)
    db.session.query(Exercise).filter(Exercise.workout_type_id == workout_type_id).delete()
    db.session.delete(workout_type)
    if not db.session.commit():
        flash('Тип удалён', category='success')
    else:
        flash('Ошибка удаления', category='error')
    return redirect(url_for('show_exercises'))


@app.route('/workout/add', methods=['POST', 'GET'])
@login_required
def add_workout() -> Response | str:
    """
    Add a new workout.

    :return: Redirect to the start of the new set for the new workout or HTML page displaying the new workout.
    """
    user_id = current_user.id
    types = [wt[0] for wt in db.session.execute(
        db.select(WorkoutType).filter(WorkoutType.user_id == user_id).order_by(WorkoutType.type)).all()]
    targets = db.session.execute(
        db.select(Target).filter(Target.user_id == user_id).order_by(Target.title)).scalars()
    if not types:
        return redirect(url_for('add_workout_type'))

    if request.method == 'POST':
        user_id = current_user.id
        workout = Workout(user_id=user_id, workout_type_id=request.form['type'],
                          date=datetime.datetime.now().replace(microsecond=0),
                          target_id=request.form['target'])
        db.session.add(workout)
        if not db.session.commit():
            flash('Начало тренировки', category='success')
            if request.form['action'] == 'Продолжить тренировку':
                return redirect(url_for('start_set'))
            elif request.form['action'] == 'Создать новую тренировку':
                return redirect(url_for('start_new_set'))
        else:
            flash('Ошибка добавления', category='error')
    return render_template('workout/add_workout.html', title='Тренировка', menu=menu, types=types, targets=targets)


@app.route('/workout/<int:workout_id>')
@login_required
def show_workout(workout_id: int) -> str:
    """
    Show the current workout.

    :param workout_id:
    :return: HTML page displaying the current workout.
    """
    workout = db.get_or_404(Workout, workout_id)
    workout_sets = workout.sets
    workout_sets.sort(key=lambda x: x.index)
    grouped_sets = groupby(workout_sets, lambda x: x.exercise.title)
    context = {
        'menu': menu,
        'grouped_sets': grouped_sets,
        'workout_id': workout_id,
        'header': f'Тренировка от {workout.date.strftime("%d.%m.%Y")}'
    }
    return render_template('workout/show_workout.html', **context)


@app.route('/workout/stop', methods=['GET', 'POST'])
@login_required
def stop_workout() -> Response | str:
    """
    Stop the current workout.

    :return: Redirect to the list of workouts page.
    """
    current_workout = db.session.execute(db.select(Workout).order_by(desc(Workout.date))).first()[0]
    current_workout.stop = datetime.datetime.now().replace(microsecond=0)
    current_workout.duration = current_workout.stop - current_workout.date
    if not db.session.commit():
        for item in menu:
            if item['name'] == 'Прод..':
                item['name'] = 'Старт'
                item['url'] = 'start_new_set'
        flash('Завершение тренировки', category='success')
        return redirect(url_for('show_workouts'))
    else:
        flash('Ошибка добавления', category='error')


@app.route('/workout/list')
@login_required
def show_workouts() -> str:
    """
    List all workouts for current user
    :return: HTML page displaying the list of workouts.
    """
    user_id = current_user.id
    workouts = db.session.query(Workout).filter_by(user_id=user_id).order_by(Workout.date).all()
    return render_template('workout/workouts.html', workouts=workouts, title='Список тренировок', menu=menu)


@app.route('/workout/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id: int) -> Response | str:
    """
    Delete a workout and its associated sets.

    :param workout_id: The ID of the workout to be deleted.
    :return: Redirect to the list of workouts page.
    """
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


@app.errorhandler(401)
def access_denied(error: Exception) -> Tuple[str, int]:
    """
    Error handler for 401 Unauthorized status.

    :param error: The exception object representing the error.
    :return: Rendered template for the unauthorized access page with a 401 status code.
    """
    return render_template('page401.html', title='Доступ запрещён', menu=menu), 401


@app.errorhandler(404)
def page_not_found(error: Exception) -> Tuple[str, int]:
    """
    Error handler for 404 Not Found status.

    :param error: The exception object representing the error.
    :return: Rendered template for the page not found page with a 404 status code.
    """
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


if __name__ == '__main__':
    # app.run(debug=True)
    # app.run(debug=True, host='192.168.31.254', port=5000)
    app.run(debug=True, host='192.168.31.5', port=5000)
    # app.run(debug=True, host='192.168.31.5')
    # app.run(host='192.168.31.5', port=5000)
    # app.run()
