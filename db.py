from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, Text, ForeignKey, DateTime, Time

# Подключение к серверу PostgreSQL на localhost с помощью psycopg2 DBAPI
engine = create_engine('postgresql+psycopg2://postgres@localhost/workouts')
engine.connect()

metadata = MetaData()

user = Table('users', metadata,
             Column('id', Integer(), primary_key=True),
             Column('name', String(25), nullable=False),
             )

workouts = Table('workouts', metadata,
                 Column('id', Integer(), primary_key=True),
                 Column('date', DateTime(), default=datetime.now),
                 Column('duration', Time()),
                 Column('user_id', ForeignKey('users.id')),
                 )

sets = Table('sets', metadata,
             Column('id', Integer(), primary_key=True),
             Column('reps', Integer()),
             Column('weight', Float()),
             Column('workout_id', ForeignKey('workouts.id')),
             Column('exercise_id', ForeignKey('exercises.id')),
             Column('duration', Time()),
             Column('rest', Time()),
             )

exercises = Table('exercises', metadata,
                  Column('id', Integer(), primary_key=True),
                  Column('title', String(100), nullable=False),
                  )

metadata.create_all(engine)
