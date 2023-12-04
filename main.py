from flask import Flask, render_template, url_for

app = Flask(__name__)
menu = ['Новая тренировка', 'Список тренировок', 'Добавить упражнение']


@app.route('/add_exercise')
def add_exercise():
    return render_template('add_exercise.html', title='Add Exercise', menu=menu)


# @app.route("/profile/<int:username>/<path>")
# def user(username, path):
#     return f'Пользователь: {username} {path}'
@app.route('/user/<username>')
def user(username):
    return f'Пользователь: {username}'


with app.test_request_context():
    print(url_for('index'))
    print(url_for('about'))
    print(url_for('user', username="selfedu"))

if __name__ == '__main__':
    app.run(debug=True)
