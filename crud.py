from datetime import datetime, timedelta

from sqlalchemy import create_engine, text, select, desc
from sqlalchemy.orm import sessionmaker, joinedload
from db import User, Workout, Exercise, Set

engine = create_engine('postgresql+psycopg2://postgres@localhost/workouts')
# session = Session(bind=engine)

Session = sessionmaker(bind=engine)


def m():
    with Session() as session:
        last_workouts = session.query(Workout).options(joinedload(Workout.sets).joinedload(Set.exercise)).filter(
            Workout.user_id == 1).filter(
            Workout.workout_type_id == 4).order_by(desc(Workout.date)).limit(4).all()
        last_workout = last_workouts[0]
        print(last_workout.date)
        new_set = Set(
            # Здесь должны быть установлены атрибуты Set, например:
            exercise_id=27,
            reps=20,
            weight=0,
            index=26,
            start=last_workout.date,
            duration=timedelta(seconds=60),
            rest=timedelta(seconds=60),

        )

        # Добавляем новый set в коллекцию sets последней тренировки
        last_workout.sets.append(new_set)

        session.commit()


def test():
    with Session() as session:
        u1 = User(name='Earl')
        u2 = User(name='Mea')
        session.add(u1)
        session.add(u2)

        w1 = Workout(user_id=1)  # create
        session.add(w1)

        e1 = Exercise(title='Push-ups')
        session.add(e1)

        s1 = Set(reps=5, weight=10, workout_id=1, exercise_id=1)
        session.add(s1)

        # session.add_all([u1, u2, w1, e1, s1])

        session.get(Set, 1).duration = timedelta(seconds=45)  # update
        # print(session.new)
        session.delete(u2)  # delete

        session.commit()
