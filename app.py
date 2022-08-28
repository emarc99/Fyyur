#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import desc
import pytz
# import datetime
from models import Venue, Artist, Show, db, datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

utc = pytz.UTC
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    unique_venues = [
        venue
        for venue in db.session.query(Venue)
        .distinct(Venue.state, Venue.city).all()
    ]

    for venue in unique_venues:
        data.append(
            {
                "city": venue.city,
                "state": venue.state,
                "venues": [
                    {
                        "id": next_venue.id,
                        "name": next_venue.name,
                        "num_upcoming_show": db.session.query(Show)
                        .filter(
                            Show.start_time
                            > datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
                        )
                        .count(),
                    }
                    for next_venue in db.session.query(Venue).filter(
                        Venue.state == venue.state, Venue.city == venue.city
                    )
                ],
            }
        )

    return render_template('pages/venues.html', areas=data)

#  Search Venue
#  ----------------------------------------------------------------


@app.route('/venues/search', methods=['POST'])
def search_venues():
    venues = (
        db.session.query(Venue)
        .filter(Venue.name.ilike(f"%{request.form.get('search_term')}%"))
        .all()
    )

    response = {
        "count": len(venues),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": db.session.query(Show)
                .filter(
                    Show.start_time
                    > datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                )
                .count(),
            }
            for venue in venues
        ],
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  Show Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    if (len(Venue.query.filter_by(id=venue_id).all()) != 0):
        past = []
        for show in Show.query.filter(Show.venue_id == venue_id).order_by(desc(Show.start_time)).limit(10):
            if show.start_time < utc.localize(datetime.now()):
                past.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter(Artist.id == show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter(Artist.id == show.artist_id).first().image_link,
                    "start_time": show.start_time.strftime("%c")
                })
        upcoming_show = []
        for show in Show.query.filter(Show.venue_id == venue_id).order_by(desc(Show.start_time)).limit(10):
            if show.start_time > utc.localize(datetime.now()):
                upcoming_show.append({
                    "artist_id": show.artists_id,
                    "artist_name": Artist.query.filter(Artist.id == show.artists_id).first().name,
                    "artist_image_link": Artist.query.filter(Artist.id == show.artists_id).first().image_link,
                    "start_time": show.start_time.strftime("%c")
                })

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website_link": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past,
            "upcoming_shows": upcoming_show,
            "past_shows_count": len(past),
            "upcoming_shows_count": len(upcoming_show)
        }
        data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
        return render_template('pages/show_venue.html', past_shows=past, upcoming_shows=upcoming_show, venue=data)

    else:
        flash('Venue does not exist')
        return redirect(url_for('venues'))

#  Update Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.facebook_link.data = venue.facebook_link
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form.get('facebook_link')
        venue.seeking_description = request.form.get('seeking_description')
        venue.image_link = request.form.get('image_link')
        venue.website = request.form.get('website')
        db.session.commit()
        flash('Venue ' + venue.name + ' has been successfully updated !')

    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm(request.form)
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm(request.form)

    try:
        venue = Venue(
            name=venue_form.name.data,
            city=venue_form.city.data,
            state=venue_form.state.data,
            address=venue_form.address.data,
            phone=venue_form.phone.data,

            # convert byte array to string separated by commas
            genres=",".join(venue_form.genres.data),
            facebook_link=venue_form.facebook_link.data,
            image_link=venue_form.image_link.data,
            seeking_talent=venue_form.seeking_talent.data,
            seeking_description=venue_form.seeking_description.data,
            website_link=venue_form.website_link.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue, ' + venue.name + ', was successfully listed!')

    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue, ' +
              venue.name + ', could not be listed.')

    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')

    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' can not be deleted.')

    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():

    data = db.session.query(Artist.id, Artist.name).all()

    return render_template('pages/artists.html', artists=data)

#  Search Artist
#  ----------------------------------------------------------------


@app.route('/artists/search', methods=['POST'])
def search_artists():

    artists = (
        db.session.query(Artist).filter(Artist.name.ilike(f"%{request.form['search_term']}%"))
        .all()
    )
    response = {
        "count": len(artists),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": db.session.query(Show)
                .filter(
                    Show.start_time
                    > datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                )
                .count(),
            }
            for artist in artists
        ],
    }
    return render_template("pages/search_artists.html", results=response, search_term=request.form.get("search_term", ""), )
    
#  Show Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)
    if (len(Artist.query.filter_by(id=artist_id).all()) != 0):
        past = []
        for show in Show.query.filter(Show.artist_id == artist_id).order_by(desc(Show.start_time)).limit(10):
            if show.start_time < utc.localize(datetime.now()):
                past.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter(Venue.id == show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter(Venue.id == show.venue_id).first().image_link,
                    "start_time": show.start_time.strftime("%c")

                })
        upcoming_show = []
        for show in Show.query.filter(Show.artist_id == artist_id).order_by(desc(Show.start_time)).limit(10):
            if show.start_time > utc.localize(datetime.now()):
                upcoming_show.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter(Venue.id == show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter(Venue.id == show.venue_id).first().image_link,
                    "start_time": show.start_time.strftime("%c")
                })

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website_link": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past,
            "upcoming_shows": upcoming_show,
            "past_shows_count": len(past),
            "upcoming_shows_count": len(upcoming_show)
        }
        data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
        return render_template('pages/show_artist.html', past_shows=past, upcoming_shows=upcoming_show, artist=data)
    else:
        flash('Artist does not exist')
        return redirect(url_for('artists'))

#  Update Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')
        artist.website_link = request.form.get('website_link')
        db.session.commit()
        flash('Artist ' + artist.name + ' has been successfully updated !')

    except Exception:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              artist.name + ' could not be updated.')

    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm(request.form)
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    artist_form = ArtistForm(request.form)

    try:
        artist = Artist(
            name=artist_form.name.data,
            city=artist_form.city.data,
            state=artist_form.state.data,
            phone=artist_form.phone.data,

            # convert byte array to string separated by commas
            genres=",".join(artist_form.genres.data),
            facebook_link=artist_form.facebook_link.data,
            image_link=artist_form.image_link.data,
            seeking_venue=artist_form.seeking_venue.data,
            seeking_description=artist_form.seeking_description.data,
            website_link=artist_form.website_link.data
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    shows = Show.query.all()

    data = []
    for show in shows:
        dict = {}
        dict["venue_id"] = show.venue.id
        dict["venue_name"] = show.venue.name
        dict["artist_id"] = show.artist.id
        dict["artist_name"] = show.artist.name
        dict["artist_image_link"] = show.artist.image_link
        dict["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        data.append(dict)

    return render_template('pages/shows.html', shows=data)

#  Create Shows
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_form = ShowForm(request.form)

    try:
        show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )
        check_show = Show.query.filter_by(
            venue_id=show.venue_id, artist_id=show.artist_id, start_time=show.start_time).all()
        if len(check_show) == 0:
            db.session.add(show)
            db.session.commit()
            flash('New show successfully listed!')
        else:
          flash('This artist already has another show booked for the same time. Please pick later of  show')
          return render_template('forms/new_show.html', form=show_form)

    except Exception:
        db.session.rollback()
        flash('An error occurred. Show failed to be listed.')

    finally:
        db.session.close()

    return redirect(url_for("index"))

# Error Handling
#  ----------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
