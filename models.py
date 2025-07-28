# models.py
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import date, time


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    hourly_wage = db.Column(db.Float, default=35.0)
    tax_credit_points = db.Column(db.Float, default=2.25)
    deductions = db.Column(db.JSON, default={})
    shifts = db.relationship('Shift', backref='user', lazy=True)


class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    note = db.Column(db.Text)
