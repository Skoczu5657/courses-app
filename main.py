# app.py - Główna aplikacja Flask

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konfiguracja bazy danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model bazy danych
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    slots = db.Column(db.Integer, nullable=False)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# Strona główna
@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

# Endpoint API: Pobierz listę kursów
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{'id': course.id, 'name': course.name, 'description': course.description, 'slots': course.slots} for course in courses])

# Formularz dodawania kursu (tylko dla administratora)
@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        slots = request.form['slots']
        
        new_course = Course(name=name, description=description, slots=int(slots))
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_course.html')

# Formularz rejestracji uczestnika
@app.route('/register/<int:course_id>', methods=['GET', 'POST'])
def register(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if course.slots > 0:
            participant = Participant(name=name, email=email, course_id=course_id)
            db.session.add(participant)
            course.slots -= 1
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return "Nie ma już wolnych miejsc!"

    return render_template('register.html', course=course)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)