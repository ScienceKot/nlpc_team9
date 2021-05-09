# Importing all needed libraries.
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from .search import find_top_n
import pickle
import numpy as np
import pandas as pd

vectorizer = pickle.load(open('vectorizer.obj', 'rb'))

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
auth = Blueprint('auth', __name__)

migrate=Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    company = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return str(self.id)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    resume = db.Column(db.String(10000), unique=False, nullable=False)

    def __repr__(self):
        return str(self.id)

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(10000), unique=False, nullable=False)
    creator = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return str(self.id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login-recruiter', methods=['GET'])
def login_recruiter():
    return render_template('login-recruiter.html')

@app.route('/register', methods=['GET'])
def signup():
    return render_template('sign-up.html')

@app.route('/profile/<id>', method=['GET'])
def profile(id):
    recruiter = Recruiter.query.filter_by(id=id).first()
    jobs = JobListing.query.filter_by(creator=id)
    return render_template('profile.html', name=recruiter.name, company=recruiter.company, jobs=jobs)

@app.route('/add-job/<id>', method=['GET', 'POST'])
def job(id):
    if request.method == 'GET':
        return render_template('add-job.html', id=id)
    else:
        creator = id
        description = request.form.get('description')

        job_listing = JobListing(description=description, creator=creator)

        db.session.add(job_listing)
        db.session.commit()

        last_joblist = JobListing.query.filter_by(description=description).first()

        if last_joblist:
            return redirect(url_for('results', id=last_joblist.id))

@app.route('/results/<id>', methods=['GET'])
def results(id):
    last_joblist = JobListing.query.filter_by(id=id).first()

    text = last_joblist.description

    records = Resume.query.with_entities(Resume.description, Resume.name, Resume.email).all()

    records = np.array([list(record) for record in records])

    X = vectorizer.transform(records[:, 0])
    text_vectorized = vectorizer.transform([text]).toarray()[0][0]

    top_5 = find_top_n(text_vectorized, X)

    return render_template('results.html', names=records[top_5, 1], email=records[top_5, 2])


@app.route('/signup-recruiter', methods=['POST'])
def signup_recruiter():
    email = request.form.get('email')
    name = request.form.get('name')
    company = request.form.get('company')

    recruiter = Recruiter.query.filter_by(email=email).first()

    if recruiter:
        return redirect(url_for('signup_recruiter'))

    new_recruiter = Recruiter(email=email, name=name, company=company)

    db.session.add(new_recruiter)
    db.session.commit()
    id = Recruiter.query.filter_by(email=email).first().id
    return redirect(url_for('profile_recruiter', id=id))

@app.route('/add-resume', methods=['GET', 'POST'])
def add_resume():
    if request.method == 'GET':
        return render_template('add-resume.html')
    else:
        email = request.form.get('email')
        name = request.form.get('name')
        description = request.form.get('description')

        new_resume = Resume(email=email, name=name, description=description)

        db.session.add(new_resume)
        db.session.commit()

        return render_template(url_for('index'))

@auth.route('/login-recruiter', methods=['POST'])
def login_recruiter():
    email = request.form.get('email')

    recruiter = Recruiter.query.filter_by(email=email).first()

    if not recruiter:
        return redirect(url_for('auth.login'))

    return redirect(url_for('main.recruiter_profile'))

