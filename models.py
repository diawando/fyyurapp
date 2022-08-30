from enum import unique
from multiprocessing.dummy import Array
import string
from sqlalchemy import func
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, String, UniqueConstraint
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

app = Flask(__name__)

db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))
    genres = db.Column(ARRAY(String))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venues', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))
    genres = db.Column(ARRAY(String))
    facebook_link = db.Column(db.String(120), unique=True)
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artists', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__='shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    