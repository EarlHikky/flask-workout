from datetime import datetime

from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, Text, ForeignKey, DateTime, Time
from sqlalchemy.orm import relationship

# Подключение к серверу PostgreSQL на localhost с помощью psycopg2 DBAPI
engine = create_engine('postgresql+psycopg2://postgres@localhost/workouts')
# engine = create_engine('sqlite:////home/earl/PycharmProjects/flask-workout/database.db')
Base = declarative_base()
# Создание таблицы (если ее нет)
Base.metadata.create_all(engine)
engine.connect()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)


class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    title = Column(String(25), unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))

class WorkoutType(Base):
    __tablename__ = 'workout_types'
    id = Column(Integer, primary_key=True)
    type = Column(String(25), unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))


class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    workout_type_id = Column(String(25), ForeignKey('workout_types.id', ondelete='CASCADE'))
    type = relationship('WorkoutType', backref='exercises')
    target_id = Column(Integer, ForeignKey('targets.id'))



class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime())
    workout_type_id = Column(String(25), ForeignKey('workout_types.id'))
    stop = Column(DateTime())
    type = relationship('WorkoutType')
    duration = Column(Time())
    user_id = Column(Integer, ForeignKey('users.id'))
    sets = relationship('Set', backref='workout')
    target_id = Column(Integer, ForeignKey('targets.id'))


class Set(Base):
    __tablename__ = 'sets'
    id = Column(Integer, primary_key=True)
    index = Column(Integer())
    reps = Column(Integer())
    weight = Column(Float())
    workout_id = Column(Integer, ForeignKey('workouts.id'))
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    exercise = relationship('Exercise')
    start = Column(DateTime())
    stop = Column(DateTime())
    duration = Column(Time())
    rest = Column(Time())


Base.metadata.create_all(engine)
