from datetime import datetime

from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, Text, ForeignKey, DateTime, Time
from sqlalchemy.orm import relationship

# Подключение к серверу PostgreSQL на localhost с помощью psycopg2 DBAPI
engine = create_engine('postgresql+psycopg2://postgres@localhost/workouts')
engine.connect()

Base = declarative_base()



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)


class WorkoutType(Base):
    __tablename__ = 'workout_types'
    id = Column(Integer, primary_key=True)
    type = Column(String(25), unique=True)

    def __repr__(self):
        return self.type


class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    workout_type_id = Column(String(25), ForeignKey('workout_types.id'))
    type = relationship('WorkoutType')


class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(), default=datetime.now)
    workout_type_id = Column(String(25), ForeignKey('workout_types.id'))
    stop = Column(DateTime())
    type = relationship('WorkoutType')
    duration = Column(Time())
    user_id = Column(Integer, ForeignKey('users.id'))
    sets = relationship('Set', backref='workout')


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
    stop = Column(DateTime(), default=datetime.now)
    duration = Column(Time())
    rest = Column(Time())


Base.metadata.create_all(engine)
