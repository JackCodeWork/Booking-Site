# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.sql import expression

from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))

    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))

    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,

        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def show_info(self):
        return {
            "id": self.id,
            "artist_id": self.artist_id,
            "venue_id": self.venue_id,
            "start_time": str(self.start_time),
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    areas = Venue.query.distinct('state', 'city').order_by('state', 'city').all()
    for area in areas:
        area.venues = Venue.query.filter_by(state=area.state, city=area.city)
    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists wFFFFFFith partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_item = request.form.get('search_term', '')
    search_item = '%' + search_item + '%'
    search_results = Venue.query.filter(Venue.name.ilike(search_item)).all()
    count = len(search_results)
    data = [result for result in search_results]
    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    data = venue.dictionary()

    past = list(filter(lambda x: x.start_time < datetime.now(), venue.shows))
    upcoming = list(filter(lambda x: x.start_time >= datetime.now(), venue.shows))
    past_shows = list(map(lambda x: x.show_info(), past))
    upcoming_shows = list(map(lambda x: x.show_info(), upcoming))

    # add upcoming/past show info to data dictionary
    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["num_past_shows"] = len(past_shows)
    data["num_upcoming_shows"] = len(upcoming_shows)
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(meta={"csrf": False})

    if not form.validate_on_submit():
        errors = form.errors
        for error in errors.values():
            flash(error[0])
        return redirect(url_for('create_venue_form'))

    error = False
    data = request.form

    try:
        new_venue = Venue(
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('state'),
            address=data.get('address'),
            phone=data.get('phone'),
            image_link=data.get('image_link'),
            facebook_link=data.get('facebook_link'),
            genres=data.getlist('genres'),

        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

        # on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Venue ' +
              data['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        shows = Show.query.filter_by(venue_id=venue_id)
        for show in shows:
            show.delete()

        venue = Venue.query.get(venue_id)
        venue.delete()
        flash('Venue deleted!')
        return render_template('pages/home.html')
    except():
        error = True
        db.session.rollback()
        flash('An error occured. Venue could not be deleted')
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data=Artist.query.order_by('id').all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    results = Artist.query.order_by(Artist.id).filter(Artist.name.ilike('%{}%'.format(search_term))).all()

    response = {'count': len(results), 'data': results}
    return render_template('pages/search_artists.html', results=response)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    data = artist.dictionary()

    # establish if show is past/upcoming
    past = list(filter(lambda x: x.start_time < datetime.now(), artist.shows))
    upcoming = list(filter(lambda x: x.start_time >= datetime.now(), artist.shows))
    past_shows = list(map(lambda x: x.show_info(), past))
    upcoming_shows = list(map(lambda x: x.show_info(), upcoming))

    # add upcoming/past show info to data dictionary
    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["num_past_shows"] = len(past_shows)
    data["num_upcoming_shows"] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(meta={"csrf": False})
    artist = Artist.query.get(artist_id).dictionary()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(meta={"csrf": False})
    if not form.validate_on_submit():
        errors = form.errors
        for error in errors.values():
            flash(error[0])
        return redirect(url_for('edit_artist', artist_id=artist_id))

    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    error = False
    data = request.form

    try:
        artist.name = data.get('name'),
        artist.city = data.get('city'),
        artist.state = data.get('state'),
        artist.phone = data.get('phone'),
        artist.image_link = data.get('image_link'),
        artist.facebook_link = data.get('facebook_link'),
        artist.genres = data.getlist('genres'),

        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + data['name'] + ' was successfully updated!')
    except():
        db.session.rollback()
        error = True
        # on unsuccessful db insert, flash an error
        flash('An error occurred. Artist' +
              data['name'] + ' could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm()
    venue = Venue.query.get(venue_id).dictionary()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(meta={"csrf": False})
    if not form.validate_on_submit():
        errors = form.errors
        for error in errors.values():
            flash(error[0])
        return redirect(url_for('edit_venue', venue_id=venue_id))

    error = False
    data = request.form
    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

    try:
        venue.name = data.get('name'),
        venue.city = data.get('city'),
        venue.state = data.get('state'),
        venue.address = data.get('address'),
        venue.phone = data.get('phone'),
        venue.image_link = data.get('image_link'),
        venue.facebook_link = data.get('facebook_link'),
        venue.genres = data.getlist('genres'),

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + data['name'] + ' was successfully updated!')
    except():
        db.session.rollback()
        error = True
        # on unsuccessful db insert, flash an error
        flash('An error occurred. Venue' +
              data['name'] + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(meta={"csrf": False})
    if not form.validate_on_submit():
        errors = form.errors
        for error in errors.values():
            flash(error[0])
        return redirect(url_for('create_artist_form'))
    error = False
    data = request.form

    try:
        new_artist = Artist(
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('state'),
            phone=data.get('phone'),
            image_link=data.get('image_link'),
            facebook_link=data.get('facebook_link'),
            genres=data.getlist('genres'),

        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except():
        db.session.rollback()
        error = True
        # on unsuccessful db insert, flash an error
        flash('An error occurred. Artist' +
              data['name'] + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = list(map(Show.show_info, shows))
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error=False
    data=request.form

    try:
        new_show=Show(
            artist_id=data.get('artist_id'),
            venue_id=data.get('venue_id'),
            start_time=data.get('start_time')
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except():
        db.session.rollback()
        error=True
        flash('An error occurred. New show could not be listed.')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
