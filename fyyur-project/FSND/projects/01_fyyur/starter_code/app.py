'''
    NOTE FROM THE STUDENT:

    You must add all genres manually for this code to work. Originally,
    genres was proposed to be a column of type list in the Artist/Venue
    models. However, this may violate some of the principles of data
    normalization. In addition, it would've made more complicated to perform
    queries such as "Select all artists who play Rock" - which is a nice
    feature I added to the app.

    In my model, the Genres Class is used as a reference table only.
    If you are interested in learning  more about why I chose this model,
    please check the following discussion:

    https://knowledge.udacity.com/questions/484042


    Once you have your database running, open python3 in a terminal window,
    then copy/paste the following code:

    ----------------------------------------------------------------------
    from app import db, Genres

    genres = ['Alternative', 'Blues', 'Classical', 'Country', 'Electronic',
    'Folk', 'Funk', 'Hip-Hop', 'Heavy Metal', 'Instrumental', 'Jazz',
    'Musical Theatre', 'Pop', 'Punk', 'R&B', 'Reggae', 'Rock n Roll',
    'Soul', 'Other']

    for g in genres:
        new_genre = Genres(name=g)
        db.session.add(new_genre)
    db.session.commit()
    db.session.close()

    ------------------------------------------------------------------------

    Now should be able to start using Fyyer from your favority browser!

'''

# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#


import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect,\
                  url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm, CSRFProtect
from forms import *
from flask_migrate import Migrate
import sys


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
#  Models - Relationship Summary:

#   Many-to-Many
#     Users ---< user_genre >--- Genres
#
#   One-to-One
#     Users --- Venues --- Shows
#     Users --- Artists --- Shows
#
#
# ----------------------------------------------------------------------------#


class User_genre(db.Model):

    __tablename__ = 'user_genre'

    user_id = db.Column(db.Integer,
                        db.ForeignKey('User.id', ondelete='cascade'),
                        primary_key=True)

    genre_id = db.Column(db.Integer,
                         db.ForeignKey('Genre.id', ondelete='cascade'),
                         primary_key=True)

    def __repr__(self):
        return f'user_id: {self.user_id} genre_id {self.genre_id}'


class Users(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(6), nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120)) #  optional to the user
    image_link = db.Column(db.String(500), default=None)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))

    genres = db.relationship('User_genre',
                             backref=db.backref('user', lazy=True),
                             cascade='save-update, merge,\
                                      delete,delete-orphan',
                             passive_deletes=True)

    venue = db.relationship('Venues',
                            backref='user',
                            uselist=False,  # ensures 1 to 1 relationship
                            cascade='all, delete',
                            passive_deletes=True
                            )

    artist = db.relationship('Artists',
                             backref='user',
                             uselist=False,
                             cascade='all, delete',
                             passive_deletes=True
                             )

    def __repr__(self):
        return f'<ID: {self.id} User Type: {self.type} {self.name}>'


class Genres(db.Model):
    """ The Genres class is used as a reference table only and must be manually
    populated before running the app. It serves as child table in the
    many-to-many relationship:

    Users--< user_genre >--Genres

    We took this approach because it was the only way to not recreate records
    with the same value every time a new User was created and therefore
    associeted with a particular genre. """

    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    users = db.relationship('User_genre',
                            backref=db.backref('genre', lazy=True),
                            cascade='all, delete',
                            passive_deletes=True)

    def __repr__(self):
        return f'<id: {self.id} Genre: {self.name}'


class Venues(db.Model):
    __tablename__ = 'Venue'

    user_id = db.Column(db.Integer,
                        db.ForeignKey('User.id', ondelete='cascade'),
                        primary_key=True)
    address = db.Column(db.String(150), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Shows',
                            backref='venue',
                            cascade='all, delete',
                            passive_deletes=True)

    def __repr__(self):
        return f'<Venue - User ID: {self.user_id} {self.address}>'


class Artists(db.Model):
    __tablename__ = 'Artist'

    user_id = db.Column(db.Integer,
                        db.ForeignKey('User.id', ondelete='cascade'),
                        primary_key=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Shows',
                            backref='artist',
                            cascade='all, delete',
                            passive_deletes=True)

    def __repr__(self):
        return f'<Artist - User ID: {self.user_id}>'


class Shows(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)

    artist_id = db.Column(db.Integer,
                          db.ForeignKey('Artist.user_id', ondelete='cascade'),
                          nullable=False)
    artist_name = db.Column(db.String(50), nullable=False)
    artist_image_link = db.Column(db.String(500))

    venue_id = db.Column(db.Integer,
                         db.ForeignKey('Venue.user_id', ondelete='cascade'),
                         nullable=False)
    venue_name = db.Column(db.String(50), nullable=False)
    venue_image_link = db.Column(db.String(500))
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


todays_datetime = datetime(datetime.today().year,
                           datetime.today().month,
                           datetime.today().day)


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Supporting Functions. By @Frodriguez9 (GitHub)
# ----------------------------------------------------------------------------#


def roll_back_db_session():
    db.session.rollback()
    print("EXCEPTION DETECTED")
    print(sys.exc_info())  # can provide usefull info for debuging
    return True  # This will set error vsariable to TRUE


def add_data_from_form(form, templete):
    '''
     This funtion is to request data from a FORM and manipulate the database
     accordingly to create new users. Called in the following routes:
     '/venues/create', methods=['POST']
     '/artists/create', methods=['POST']
     '''

    error = False
    form = form

    if not form.validate_on_submit():
        return render_template(templete,
                               form=form,
                               error='User could not be listed')
    else:
        is_seeking = False
        if isinstance(form, VenueForm):
            type = "Venue"
            if form.seeking_talent.data == 'Yes':
                is_seeking = True
            new_type = Venues(address=form.address.data,
                              seeking_talent=is_seeking)

        elif isinstance(form, ArtistForm):
            type = "Artist"
            if form.seeking_venue.data == 'Yes':
                is_seeking = True
            new_type = Artists(
                        seeking_venue=is_seeking,
                        seeking_description=form.seeking_description.data)

    try:
        new_user = Users(type=type,
                         name=form.name.data,
                         city=form.city.data,
                         state=form.state.data,
                         phone=form.phone.data,
                         image_link=form.image_link.data,
                         facebook_link=form.facebook_link.data,
                         website=form.website.data)

        new_type.user = new_user

        user_genres = []
        genres_submition = form.genres.data  # returns a list
        for i in genres_submition:
            genre = Genres.query.filter(Genres.name == i).one()
            user_genres.append(User_genre(genre_id=genre.id))

        new_user.genres = user_genres

        db.session.add(new_user)
        db.session.commit()
    except:
        error = roll_back_db_session()
    finally:
        db.session.close()

    if error:
        return render_template(templete,
                               form=form,
                               error=type + ' could not be listed')

    else:
        flash(type + ' ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))


def delete_user(user_id):
    error = False
    try:
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()
    except:
        error = roll_back_db_session()
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        flash('User successfully deleted')
        return redirect(url_for('index'))


def update_user(user_type, user_id, form, user_query,
                additional_query, url_str_for_return):
    user_type = user_type
    user_id = user_id
    form = form
    user_info = user_query
    user_additional_info = additional_query

    error = False

    try:
        user_info.name = form.name.data,
        user_info.city = form.city.data,
        user_info.state = form.state.data,
        user_info.phone = form.phone.data,
        user_info.image_link = form.image_link.data,
        user_info.facebook_link = form.facebook_link.data,
        user_info.website = form.website.data,

        old_genres = User_genre.query.filter(User_genre.user_id == user_id)\
                                     .delete()

        user_genres = []
        genres_submition = form.genres.data
        for i in genres_submition:
            genre = Genres.query.filter(Genres.name == i).one()
            user_genres.append(User_genre(genre_id=genre.id))

        user_info.genres = user_genres

        if user_type == 'Venue':
            user_additional_info.address = form.address.data
            if form.seeking_talent.data == "Yes":
                user_additional_info.seeking_talent = True
            else:
                user_additional_info.seeking_talent = False

        if user_type == 'Artist':
            user_additional_info.seeking_description = form.seeking_description.data
            if form.seeking_venue.data == "Yes":
                user_additional_info.seeking_venue = True
            else:
                user_additional_info.seeking_venue = False

        db.session.commit()
    except:
        error = roll_back_db_session()
    finally:
        db.session.close()

    if error:
        pass  # 'edit' route will handle the error

    else:
        flash("User successfully updated")
        return redirect(url_for(url_str_for_return, user_id=user_id))


def build_show_info(show_object):
    show_info = {}
    show_info['venue_id'] = show_object.venue_id
    show_info['venue_name'] = show_object.venue_name
    show_info['artist_id'] = show_object.artist_id
    show_info['artist_name'] = show_object.artist_name
    show_info['artist_image_link'] = show_object.artist_image_link
    show_info['start_time'] = str(show_object.start_time)

    return show_info


def count_upcoming_shows(user_id):

    ''' the model Shows hold both Artist and Venue, each with a relationship
        to the Users class with a unique user id. Hance, the condition
        (or_(Shows.artist_id == user_id, Shows.venue_id == user_id)
        makes this function flexible to be used securely for both the Artist
        route and Venue route without qurying unwanted records'''

    num_of_shows = Shows.query.filter(
        or_(Shows.artist_id == user_id, Shows.venue_id == user_id),
        Shows.start_time > todays_datetime).count()

    return num_of_shows


def query_genres(user_id):
    user_genres = []
    genres = db.session.query(User_genre, Genres)\
        .outerjoin(Genres, User_genre.genre_id == Genres.id)\
        .filter(User_genre.user_id == user_id)\
        .all()

    for genre in genres:
        user_genres.append(genre[1].name)

    return user_genres


def google(user_type, template):

    term = request.form['search_term']

    query = Users.query.filter(Users.name.ilike(f'%{term}%'),
                               Users.type == user_type)

    data = []
    for user in query.all():
        dic = {}
        dic['id'] = user.id
        dic['name'] = user.name
        dic["num_upcoming_shows"] = count_upcoming_shows(user.id)
        data.append(dic)

    response = {"count": query.count(),
                "data": data}

    return render_template(template, results=response, search_term=term)


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    latests_sign_ups = Users.query.order_by(db.desc(Users.id)).limit(10).all()

    data = []
    for user in latests_sign_ups:
        user_info = {}
        user_info['id'] = user.id
        user_info['type'] = user.type
        user_info['name'] = user.name
        user_info['image_link'] = user.image_link
        data.append(user_info)

    return render_template('pages/home.html', users=data)


# Venues
# ----------------------------------------------------------------------------#


@app.route('/venues')
def venues():
    results = db.session.query(Users)\
        .filter(Users.type == 'Venue')\
        .order_by(Users.city, Users.state).all()

    def query_location(city=None, state=None):
        location = {}
        location['city'] = city
        location['state'] = state
        location['venues'] = []
        return location

    def query_venue(id=None, venue_name=None, num_shows=None):
        venue = {}
        venue['id'] = id
        venue['name'] = venue_name
        venue['num_upcoming_shows'] = num_shows
        return venue

    '''
        The loop below creates a data structure that looks like this:

        data = [{
                'city': None,
                'state': None,
                'venues':[{ 'id': none,
                            'name': none,
                            'num_upcoming_shows': none }]
                }]
    '''

    data = []
    location = {'city': None,
                'state': None,
                'venues': None}

    for r in results:
        id = r.id
        city = r.city
        state = r.state
        venue_name = r.name
        num_of_shows = count_upcoming_shows(id)

        if not location['city']:  # handels first entry to data instance
            location = query_location(city, state)

        elif (location['city'] == city) and (location['state'] == state):
            pass  # jumps to the 'append' statement after the if block

        else:  # e.g: two different states with the same city name
            data.append(location)
            location = query_location(city, state)

        location['venues'].append(query_venue(id,
                                              venue_name,
                                              num_of_shows))

        if results.index(r) == (len(results)-1):  # handels last entry
            data.append(location)

    db.session.close()  # not sure if this closure is necessary
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    return google(user_type='Venue', template='pages/search_venues.html')


@app.route('/venues/<int:user_id>')
def show_venue(user_id):
    venue = Users.query.filter(Users.id == user_id).one()

    venue_additional_info = Venues.query.\
        filter(Venues.user_id == user_id).one()

    address = venue_additional_info.address
    is_seeking = venue_additional_info.seeking_talent

    genres_object = db.session\
        .query(Genres.name)\
        .join(User_genre, Genres.id == User_genre.genre_id)\
        .filter(User_genre.user_id == user_id).all()

    genres = []
    for g in genres_object:
        genre = g[0]
        genres.append(genre)

    shows = Shows.query.filter(Shows.venue_id == user_id).all()
    past_shows = []
    upcoming_shows = []

    for show in shows:
        show_info = {
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            }
        if show.start_time <= todays_datetime:
            show_info['start_time'] = str(show.start_time)
            past_shows.append(show_info)
        elif show.start_time > todays_datetime:
            show_info['start_time'] = str(show.start_time)
            upcoming_shows.append(show_info)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": is_seeking,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",  # Set An Account
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
      }
    db.session.close()
    return render_template('pages/show_venue.html', venue=data)

# Create Venue
# ----------------------------------------------------------------------------#


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    return add_data_from_form(VenueForm(), 'forms/new_venue.html')


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    return delete_user(venue_id)

# Artists
# ----------------------------------------------------------------------------#


@app.route('/artists')
def artists():
    artists_object = Users.query.filter(Users.type == 'Artist').all()

    artist = {}
    data = []

    for a in artists_object:
        artist = {}
        artist['id'] = a.id
        artist['name'] = a.name
        data.append(artist)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    return google(user_type='Artist', template='pages/search_artists.html')


@app.route('/artists/<int:user_id>')
def show_artist(user_id):
    artist = Users.query.filter(Users.id == user_id).one()

    artist_additional_info = Artists.query\
        .filter(Artists.user_id == user_id).one()

    is_seeking = artist_additional_info.seeking_venue
    seeking_description = artist_additional_info.seeking_description

    genres_object = db.session.query(Genres.name)\
        .join(User_genre, Genres.id == User_genre.genre_id)\
        .filter(User_genre.user_id == user_id).all()

    genres = []
    for g in genres_object:
        genre = g[0]
        genres.append(genre)

    shows = Shows.query.filter(Shows.artist_id == user_id).all()
    past_shows = []
    upcoming_shows = []

    for show in shows:
        show_info = {"venue_id": show.venue_id,
                     "venue_name": show.venue_name,
                     "venue_image_link": show.venue_image_link}

        if show.start_time <= todays_datetime:
            show_info['start_time'] = str(show.start_time)
            past_shows.append(show_info)

        elif show.start_time > todays_datetime:
            show_info['start_time'] = str(show.start_time)
            upcoming_shows.append(show_info)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": is_seeking,
        "seeking_description": seeking_description,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",  # Set An Account
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    db.session.close()  # Not sure if I have to invoke this on queries
    return render_template('pages/show_artist.html', artist=data)


# Update
# ----------------------------------------------------------------------------#


@app.route('/artists/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_artist(user_id):
    form = ArtistForm()
    user_info = Users.query.filter(Users.id == user_id).one()

    user_additional_info = Artists.query\
        .filter(Artists.user_id == user_id).one()

    genres = db.session.query(Genres)\
        .outerjoin(User_genre, Genres.id == User_genre.genre_id)\
        .filter(User_genre.user_id == user_id).all()

    artist = {"id": user_info.id,
              "name": user_info.name}

    is_seeking_talent = ''

    if user_additional_info.seeking_venue:
        is_seeking_venue = 'Yes'
    else:
        is_seeking_venue = 'No'

    if request.method == 'GET':
        form = ArtistForm(obj=user_info,
                          # populates the fields of the Users class
                          seeking_venue=is_seeking_venue,
                          # populates 'seeking_venue' which is not
                          # in the Users class but in Artist class
                          seeking_description=user_additional_info\
                          .seeking_description)
                          # populates 'seeking_description' which
                          # is not in the Users class but in Artist class)

        form.genres.data = [(g.name) for g in genres]
        # to prepopulate multiple choices

        return render_template('forms/edit_artist.html',
                               form=form, artist=artist)

    if request.method == 'POST' and form.validate_on_submit():
        return update_user('Artist', user_id, form, user_info,
                           user_additional_info, 'show_artist')

    else:
        error_message = 'Unsuccesful edit: Missing a requiered '\
                        'field or urls start without "http://"'
        return render_template('forms/edit_artist.html', form=form,
                               artist=artist, error=error_message)


@app.route('/venues/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_venue(user_id):
    form = VenueForm()
    user_info = Users.query.filter(Users.id == user_id).one()

    user_additional_info = Venues.query\
        .filter(Venues.user_id == user_id).one()

    genres = db.session.query(Genres)\
        .outerjoin(User_genre, Genres.id == User_genre.genre_id)\
        .filter(User_genre.user_id == user_id).all()

    venue = {"name": user_info.name,
             "id": user_info.id}

    is_seeking_talent = ''

    if user_additional_info.seeking_talent:
        is_seeking_talent = 'Yes'
    else:
        is_seeking_talent = 'No'

    if request.method == 'GET':
        form = VenueForm(obj=user_info,
                         # populates the fields of the Users class
                         address=user_additional_info.address,
                         # populates 'address' which is not in the
                         # Users class but in Venues class
                         seeking_talent=is_seeking_talent)
                         # populates 'seeking_talent' which
                         # is not in the Users class but in Venues class

        form.genres.data = [(g.name) for g in genres]
        # to prepopulate multiple choices

        return render_template('forms/edit_venue.html', form=form, venue=venue)

    if request.method == 'POST' and form.validate_on_submit():
        return update_user('Venue', user_id, form, user_info,
                           user_additional_info, 'show_venue')

    else:
        error_message = 'Unsuccesful edit: Missing a requiered field '\
                        'or urls start without "http://"'
        return render_template('forms/edit_venue.html', form=form,
                               venue=venue, error=error_message)

# Create Artist
# ----------------------------------------------------------------------------#


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    return add_data_from_form(ArtistForm(), 'forms/new_artist.html')


@app.route('/artists/<user_id>/delete', methods=['POST'])
def delete_artist(user_id):
    return delete_user(user_id)


# Shows
# ----------------------------------------------------------------------------#


@app.route('/shows')
def shows():
    shows = Shows.query.filter(Shows.start_time > todays_datetime)\
            .order_by(Shows.venue_id).all()

    data = []
    for show in shows:
        data.append(build_show_info(show))

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


# Create Show
# ----------------------------------------------------------------------------#


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm()

    if form.validate_on_submit():
        try:
            artist_id = form.artist_id.data
            venue_id = form.venue_id.data

            artist_info = Users.query.filter_by(id=artist_id).one()
            venue_info = Users.query.filter_by(id=venue_id).one()

            new_show = Shows(artist_id=artist_info.id,
                             artist_name=artist_info.name,
                             artist_image_link=artist_info.image_link,
                             venue_id=venue_info.id,
                             venue_name=venue_info.name,
                             venue_image_link=venue_info.image_link,
                             city=venue_info.city,
                             state=venue_info.state,
                             start_time=form.start_time.data)

            db.session.add(new_show)
            db.session.commit()
        except:
            error = roll_back_db_session()
        finally:
            db.session.close()

        if error:
            return render_template('forms/new_show.html',
                                   form=ShowForm(),
                                   error="Somthing went wrong. Make sure the "
                                         "Artist and Venue ID are correct.")
        else:
            flash('Show was successfully listed!')
            return redirect(url_for('index'))


@app.route('/shows/search', methods=["POST"])
def search_shows():
    term = request.form["search_term"]
    shows = Shows.query.filter(or_(Shows.artist_name.ilike(f'%{term}%'),
                                   Shows.venue_name.ilike(f'%{term}%'))).all()

    data = []
    for show in shows:
        data.append(build_show_info(show))

    result = {'term': term,
              'data': data,
              'count': len(data)}

    return render_template('pages/search_shows.html', results=result)


@app.route('/search_shows_advance', methods=['GET', 'POST'])
def show_advance_search():
    form = ShowSeachForm()
    if request.method == 'GET':
        return render_template('pages/search_shows_advance.html', form=form)

    if request.method == 'POST':

        artist_submition = form.artist_name.data
        venue_submition = form.venue_name.data
        city_submition = form.city.data
        state_submition = form.state.data
        start_time_submition = form.start_time.data

        '''
            The form fields return a 'str type' even if the field
            is empty. This block convert them to None type so
            the filter conditions below can be executed
        '''

        if artist_submition == '':
            artist_submition = None
        if venue_submition == '':
            venue_submition = None
        if city_submition == '':
            city_submition = None
        if state_submition == 'State':
            state_submition = None

        # Filters input -------------------------------------------------------

        artist_filter = Shows.artist_name.ilike(f'%{artist_submition}%')
        venue_filter = Shows.venue_name.ilike(f'%{venue_submition}%')
        city_filter = Shows.city.ilike(f'{city_submition}')
        state_filter = Shows.state == state_submition
        if start_time_submition:
            start_time_filter = Shows.start_time >= start_time_submition

        filters = []
        if artist_submition:
            filters.append(artist_filter)
        if venue_submition:
            filters.append(venue_filter)
        if city_submition:
            filters.append(city_filter)
        if state_submition:
            filters.append(state_filter)
        if start_time_submition:
            filters.append(start_time_filter)

        shows = Shows.query.filter(*filters).all()

        data = []
        for show in shows:
            show_info = build_show_info(show)
            data.append(show_info)

        num_results = len(data)

        # TODO Ater submission: Try to implement an AJAX query in
        # the front end instead rendering the template
        return render_template('pages/search_shows_advance.html', form=form,
                               shows=data, count=num_results)


@app.route('/advance_user_search', methods=['GET', 'POST'])
def search_user():
    form = Advance_user_search_form()
    if request.method == 'GET':
        return render_template('pages/search_users_by_filters.html', form=form)

    if request.method == 'POST':

        city_submition = form.city.data
        state_submition = form.state.data
        type_submition = form.type.data
        genres_submition = form.genres.data

    '''
        The form fields return a 'str type' even if the field
        is empty. This block convert them to None type so
        the filter conditions below can be executed
    '''

    if city_submition == '':
        city_submition = None
    if state_submition == 'State':
        state_submition = None
    if type_submition == 'type' or type_submition == 'both':
        type_submition = None

    if genres_submition == '[]':
        genres_submition = None
    else:
        genres_selection = []
        for genre in genres_submition:
            genres_selection.append(Genres.name == genre)

    # Filters input -------------------------------------------------------

    city_filter = Users.city.ilike(f'{city_submition}')
    state_filter = Users.state == state_submition
    type_filter = Users.type == type_submition
    genres_filter = or_(*genres_selection)

    filters = []
    if city_submition:
        filters.append(city_filter)
    if state_submition:
        filters.append(state_filter)
    if type_submition:
        filters.append(type_filter)
    if genres_submition:
        filters.append(genres_filter)

    query = db.session.query(Users.id,
                             Users.name,
                             Users.type,
                             Users.image_link,
                             db.func.count(User_genre.user_id))\
        .outerjoin(User_genre, Users.id == User_genre.user_id)\
        .outerjoin(Genres, User_genre.genre_id == Genres.id)\
        .filter(*filters).group_by(Users.id).all()

    ''' The following for loop furthers filters the query.
        If the user selects genres as filter, we display only the
        artists/venues that meet exactly all genres the user selected '''

    results = []
    for data in query:
        genres_count = data[4]

        user_info = {}
        user_info['id'] = data[0]
        user_info['name'] = data[1]
        user_info['type'] = data[2]
        user_info['image_link'] = data[3]

        if genres_submition:
            if genres_count == len(genres_selection):
                results.append(user_info)
        else:  # when user does not pick any genre as a filter
            results.append(user_info)

    web_data = {'results': results,
                'results_count': len(results)}

    return render_template('pages/search_users_by_filters.html',
                           form=form,
                           data=web_data)


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
