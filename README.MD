# Workout Tracker App

This is a Flask application designed to help users track their workouts and exercises. It provides functionality for adding users, exercises, and workout sets, as well as tracking workout history.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following requirements installed:

- Python 3.x
- PostgreSQL
- [Flask](https://flask.palletsprojects.com/en/2.1.x/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.x/)

### Installation

1. Clone the repository:

     git clone https://github.com/EarlHikky/flask-workout
   
2. Change into the project directory:

     cd workout-tracker-app
   
3. Install [Poetry](https://python-poetry.org/) if you haven't already:

     pip install poetry
   
4. Install the required dependencies using Poetry:

     poetry install
   
   This will read the pyproject.toml file and install the necessary packages.

5. Set up the PostgreSQL database or another database:

   - Create a PostgreSQL database named 'workouts'.
   - Update the database URI in app.config['SQLALCHEMY_DATABASE_URI'] in app.py to match your PostgreSQL configuration.

6. Run the application:

     poetry run python app.py
   
The application will be accessible at [http://localhost:5000/](http://localhost:5000/).

## Usage

### Adding a User

1. Navigate to [http://localhost:5000/user/add](http://localhost:5000/user/add).
2. Enter the user's name and submit the form.

### Starting a New Workout

1. Navigate to [http://localhost:5000/add_workout](http://localhost:5000/add_workout).
2. Choose the workout type and click on "Продолжить тренировку" or "Создать новую тренировку."

### Adding a Workout Set

1. Start a new set or continue from the last set by navigating to [http://localhost:5000/set/start](http://localhost:5000/set/start).
2. Fill in the set details and submit the form.

### Viewing Workout History

- View a list of workouts at [http://localhost:5000/workouts](http://localhost:5000/workouts).
- View details of a specific workout by clicking on its date.

## Additional Features

- Exercise management: Add, update, and delete exercises.
- Set management: View, update, and delete workout sets.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)

