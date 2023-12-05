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


class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)


class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(), default=datetime.now)
    duration = Column(Time())
    user_id = Column(Integer, ForeignKey('users.id'))
    sets = relationship('Sets', backref='workout')


class Sets(Base):
    __tablename__ = 'sets'
    id = Column(Integer, primary_key=True)
    reps = Column(Integer())
    weight = Column(Float())
    workout_id = Column(Integer, ForeignKey('workouts.id'))
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    exercise = relationship('Exercise')
    duration = Column(Time())
    rest = Column(Time())


Base.metadata.create_all(engine)
