from flask import Blueprint, render_template

exercise = Blueprint('exercise', __name__)

@exercise.route('/add-exercise', methods=['POST', 'GET'])
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

