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
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))  # "זכר"/"נקבה"
    marital_status = db.Column(db.String(10))  # "רווק"/"נשוי"
    city = db.Column(db.String(50))
    has_degree = db.Column(db.Boolean, default=False)
    degree_year = db.Column(db.Integer, nullable=True)
    hourly_wage = db.Column(db.Float, default=35.0)
    tax_credit_points = db.Column(db.Float, default=2.25)
    deductions = db.Column(db.JSON, default={})
    shifts = db.relationship('Shift', backref='user', lazy=True)
    children = db.relationship('Child', backref='parent', cascade="all, delete-orphan")

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    note = db.Column(db.Text)

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    birth_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class TaxExemptCity(db.Model):
    __tablename__ = 'tax_exempt_cities'

    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), unique=True, nullable=False)
    tax_discount_percent = db.Column(db.Float, default=0.0)
    annual_cap = db.Column(db.Float, default=0.0)

