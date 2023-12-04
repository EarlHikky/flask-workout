from flask import Flask, render_template, url_for, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
menu = [{"name": "Новая тренировка", "url": "new-workout"},
        {"name": "Список тренировок", "url": "workouts"},
        {"name": "Добавить упражнение", "url": "add-exercise"}]


# @app.route('/add-exercise')
# def add_exercise():
#     return render_template('add_exercise.html', title='Add Exercise', menu=menu)


# @app.route("/profile/<int:username>/<path>")
# def user(username, path):
#     return f'Пользователь: {username} {path}'
@app.route('/user/<username>')
def user(username):
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


# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('about'))
#     print(url_for('user', username="selfedu"))

if __name__ == '__main__':
    app.run(debug=True)
