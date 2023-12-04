from flask import Flask, render_template

app = Flask(__name__)
menu = ["Установка", "Первое приложение", "Обратная связь"]

@app.route('/add_exercise')
def add_exercise():
    return render_template('add_exercise.html', title='Add Exercise', menu = menu)


if __name__ == '__main__':
    app.run(debug=True)
