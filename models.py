#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from collections import UserList
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Venue model
# -------------------------------------

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=True, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', back_populates='venue', uselist=False)

# Artist model
# -------------------------------------

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=True, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', back_populates='artist')

# Shows model
# -------------------------------------

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)

    # Many-to-many relationship using the latest recommended method at this time
    artist = db.relationship('Artist', back_populates='shows')
    venue = db.relationship('Venue', back_populates='shows', uselist=False)
