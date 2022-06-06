from api.app import db
from flask_login import UserMixin


# Booking database model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    room = db.Column(db.String(256))
    phone = db.Column(db.String(256))
    old_code = db.Column(db.String(256))
    current_code = db.Column(db.String(256))


# Room database model
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(256))
    code = db.Column(db.String(256))


# User database model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    admin = db.Column(db.Boolean)
    email = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
