from datetime import datetime, timedelta

from sqlalchemy import create_engine, text, select, desc
from sqlalchemy.orm import sessionmaker
from db import User, Workout, Exercise, Set

engine = create_engine('postgresql+psycopg2://postgres@localhost/workouts')
# session = Session(bind=engine)

Session = sessionmaker(bind=engine)


def m(i):
    with Session() as session:
        workout = session.get_one(Workout, i)

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
