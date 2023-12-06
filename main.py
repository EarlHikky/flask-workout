import time
from pprint import pp

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, Response, jsonify
from flask_sqlalchemy import SQLAlchemy

from db import User, Exercise, Workout, Sets

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


@app.route('/user/create', methods=['GET', 'POST'])
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
def show_exercises():
    exercises = db.session.execute(db.select(Exercise).order_by(Exercise.title)).scalars()
    return render_template('exercise/exercises.html', exercises=exercises, title='Список упражнений', menu=menu)


@app.route('/workouts')
def show_workouts():
    workouts = db.session.execute(db.select(Workout).order_by(Workout.date)).scalars()
    return render_template('workout/workouts.html', workouts=workouts, title='Список тренировок', menu=menu)




@app.route('/set/create', methods=['POST', 'GET'])
def add_set():
    if request.method == 'POST':

        set = Sets(
            reps=request.form['reps'],
            weight=request.form['weight'],
#            duration=request.form['duration'],
#            rest=request.form['rest'],
        )
        db.session.add(set)
        if not db.session.commit():
            flash('Сет добавлен', category='success')
        else:
            flash('Ошибка добавления', category='error')
    return render_template('set/create.html', title='Добавить сет', menu=menu)


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





@app.route('/content') # render the content a url differnt from index. This will be streamed into the iframe
def content():
    def timer(t):
        for i in range(t):
            time.sleep(1) #put 60 here if you want to have seconds
            yield str(i)
    return Response(timer(10), mimetype='text/html') #at the moment the time value is hardcoded in the function just for simplicity



@app.route('/timer')
def timer():
    return render_template('timer.html')

@app.route('/start_timer', methods=['POST'])
def start_timer():
    global timer_id
    duration = int(request.form['duration'])
    timer_id = int(time.time())  # Уникальный идентификатор для таймера
    time.sleep(duration)
    return jsonify({'status': 'success', 'timer_id': timer_id})

@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    global timer_id
    timer_id = None
    return jsonify({'status': 'success'})




def test_request():
    with app.test_request_context():
        print(url_for('index'))
        print(url_for('about'))
        print(url_for('user', username='selfedu'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='192.168.31.5', port=5000)
    # app.run()
