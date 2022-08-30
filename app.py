#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from cmath import e
import json
from tracemalloc import start
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFError
from datetime import datetime
import pytz
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


moment = Moment(app)
app.config.from_object('config')
csrf.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

utc=pytz.UTC

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# CSRF  ERROR HANDLER
#----------------------------------------------------------------------------#
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  datas = Venue.query.join(Show, Venue.id==Show.venue_id, isouter=True).all()
  today = datetime.now().replace(tzinfo=utc)
  d = {}
  showscount = 0
  for da in datas:
    for i in range(len(da.shows)):
          if da.shows[i].start_time > today:
            showscount +=1
    if da.city not in d.keys():
      d[da.city] = {
        "city" : da.city,
        "state" : da.state,
        "venues":[{
          "id": da.id,
          "name": da.name,
          "num_upcoming_shows":showscount, 
        }]
      }
    else:
      d[da.city]["venues"].append({
        "id":da.id,
        "name":da.name,
        "num_upcoming_shows":showscount
      })
      
            
  data = d.values()
 
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  form = VenueForm()
  search_term = request.form.get('search_term', '')
  requetes = Venue.query.filter(Venue.name.ilike('%'+ search_term + '%')).all()
  reponse = {
      "count" : 0,
      "data" : []
    }
  today = utc.localize(datetime.now())
  

  for requete in requetes:
     nombre = 0
     for i in range(len(requete.shows)):
        if requete.shows[0].start_time > today :
           nombre += 1
     reponse["count"] +=1
     reponse["data"].append({
        "id" : requete.id,
        "name" : requete.name,
        "num_upcoming_shows" : nombre
     })
  
  return render_template('pages/search_venues.html', results=reponse, search_term=search_term, form = form)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  requete = Venue.query.join(Show,Venue.id==Show.venue_id, isouter=True).join(Artist, Show.artist_id==Artist.id, isouter=True).filter(Venue.id==venue_id).first_or_404()
  today = datetime.now().replace(tzinfo=utc)
  data={
    "id": requete.id,
    "name": requete.name,
    "genres": requete.genres,
    "address": requete.address,
    "city": requete.city,
    "state": requete.state,
    "phone": requete.phone,
    "website": requete.website_link,
    "facebook_link": requete.facebook_link,
    "seeking_talent": requete.seeking_talent,
    "seeking_description": requete.seeking_description,
    "image_link": requete.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  for i in range(len(requete.shows)):
    if requete.shows[i].start_time < today:
       data["past_shows"].append(
       {
      "artist_id": requete.shows[i].artist_id,
      "artist_name": requete.shows[i].artists.name,
      "artist_image_link": requete.shows[i].artists.image_link,
      "start_time": requete.shows[i].start_time,
      }
      )
    else:
      data["upcoming_shows"].append(
       {
      "artist_id": requete.shows[i].artist_id,
      "artist_name": requete.shows[i].artists.name,
      "artist_image_link": requete.shows[i].artists.image_link,
      "start_time": requete.shows[i].start_time,
      }
      )
    data["past_shows_count"] = len(data["past_shows"])
    data['upcoming_shows_count'] = len(data["upcoming_shows"])
      
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
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
  form = VenueForm()
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      image_link = form.image_link.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
      venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres,
                    facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
      db.session.rollback()
      db.session.close()
      flash('An error occured. Venue ' + form.name.data + ' could not be listed.' + str(e))
  # e.g.,flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
      flash(form.errors)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'POST', 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  
  try:
      db.session.delete(venue)
      db.session.commit()
      db.session.close()
      flash('element has been sucessfuly deleted')
  except Exception as e:
      db.session.rollback()
      db.session.close()
      flash(str(e))
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  datas = Artist.query.all()
  d = {}
  data = []
  for da in datas:
    if da.id not in d.values() and da.name not in d.values():
      d={
        "id": da.id,
        "name": da.name,
      }
    data.append(d)
   
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  form = ArtistForm()
  search_term = request.form.get('search_term', '')
  requetes = Artist.query.join(Show, Artist.id==Show.artist_id).filter(Artist.name.ilike('%'+ search_term + '%')).all()
  today = datetime.now()
  reponse ={
      "count":0,
      "data" : []
  }
  
  today = utc.localize(datetime.now())
  
  for requete in requetes:
     nombre = 0
     if requete.shows[0].start_time > today :
        nombre += 1
     reponse["count"] +=1
     reponse["data"].append({
        "id" : requete.id,
        "name" : requete.name,
        "num_upcoming_shows" : nombre
     })
  
  return render_template('pages/search_artists.html', results=reponse, search_term=search_term, form=form)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  requete = Artist.query.join(Show, Artist.id==Show.artist_id).join(Venue, Show.venue_id==Venue.id).filter(Artist.id==artist_id).first_or_404()
  today = datetime.now().replace(tzinfo=utc)
   
  data={
    "id": requete.id,
    "name": requete.name,
    "genres": requete.genres,
    "city": requete.city,
    "state": requete.state,
    "phone": requete.phone,
    "website": requete.website_link,
    "facebook_link": requete.facebook_link,
    "seeking_venue": requete.seeking_venue,
    "seeking_description": requete.seeking_description,
    "image_link": requete.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  
  for i in range(len(requete.shows)):
      if requete.shows[i].start_time < today :
        data["past_shows"].append({
          "venue_id": requete.shows[i].venues.id,
          "venue_name": requete.shows[i].venues.name,
          "venue_image_link": requete.shows[i].venues.image_link,
          "start_time": requete.shows[i].start_time,
         })
      else:
        data["upcoming_shows"].append({
          "venue_id": requete.shows[i].venues.id,
          "venue_name": requete.shows[i].venues.name,
          "venue_image_link": requete.shows[i].venues.image_link,
          "start_time": requete.shows[i].start_time,
         })
      data["past_shows_count"] = len(data["past_shows"])
      data["upcoming_shows_count"] = len(data["upcoming_shows"])
        
 
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  requete = Artist.query.filter(Artist.id==artist_id).first_or_404()
  form.name.data = requete.name
  form.genres.data = requete.genres
  form.city.data = requete.city
  form.state.data = requete.state
  form.phone.data = requete.phone
  form.website_link.data = requete.website_link
  form.facebook_link.data = requete.facebook_link
  form.seeking_venue.data = requete.seeking_venue
  form.seeking_description.data = requete.seeking_description
  form.image_link.data = requete.image_link
  artist={
    "id": requete.id,
    "name": form.name.data,
    "genres": form.genres.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website_link.data,
    "facebook_link": form.facebook_link.data,
    "seeking_venue": form.seeking_venue.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  if form.validate_on_submit():
      try:
          artist = Artist.query.filter(Artist.id==artist_id).first()
          artist.name = form.name.data
          artist.genres = form.genres.data
          artist.city = form.city.data
          artist.state = form.state.data
          artist.phone = form.phone.data
          artist.website_link = form.website_link.data
          artist.facebook_link = form.facebook_link.data
          artist.seeking_venue = form.seeking_venue.data
          artist.seeking_description = form.seeking_description.data
          artist.image_link = form.image_link.data
          
          db.session.commit()
          db.session.close()
          
      except Exception as e:
          db.session.rollback
          db.session.close()
          flash(str(e))
          
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  requete = Venue.query.filter(Venue.id==venue_id).first_or_404()
  
  form.name.data = requete.name
  form.genres.data = requete.genres
  form.address.data = requete.address
  form.city.data = requete.city
  form.state.data = requete.state
  form.phone.data = requete.phone
  form.website_link.data = requete.website_link
  form.facebook_link.data = requete.facebook_link
  form.seeking_talent.data = requete.seeking_talent
  form.seeking_description.data = requete.seeking_description
  form.image_link.data = requete.image_link
  venue={
    "id": requete.id,
    "name": form.name.data,
    "genres": form.genres.data,
    "address": form.address.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website_link.data,
    "facebook_link": form.facebook_link.data,
    "seeking_talent": form.seeking_talent.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  if form.validate_on_submit():
    try:
       venue = Venue.query.filter(Venue.id==venue_id).first()
       venue.name = form.name.data
       venue.genres = form.genres.data
       venue.address = form.address.data
       venue.city = form.city.data
       venue.state = form.state.data
       venue.phone = form.phone.data
       venue.website_link = form.website_link.data
       venue.facebook_link = form.facebook_link.data
       venue.seeking_talent = form.seeking_talent.data
       venue.seeking_description = form.seeking_description.data
       venue.image_link = form.image_link.data
       
       db.session.commit()
       db.session.close()
       
    except Exception as e:
      db.session.rollback
      db.session.close()
      flash(str(e))

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  form = ArtistForm()
  
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      image_link = form.image_link.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      
      artist = Artist(name = name, city = city, state= state, phone = phone,
                      image_link = image_link, genres= genres, facebook_link=facebook_link,
                      website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
      
      db.session.add(artist)
      db.session.commit()
  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
      db.session.rollback()
      db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occured. Artist ' + form.name.data + ' could not be listed' + str(e))
  else :
      flash(form.errors)
    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
    requete = db.session.query(Artist, Venue, Show).join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id)
    da = {}
    data = []
    try:
      for d in requete:
        if d["Artist"].id == d["Show"].artist_id:
          da = {
           "venue_id": d["Venue"].id,
           "venue_name": d["Venue"].name,
           "artist_id": d["Artist"].id,
           "artist_name": d["Artist"].name,
           "artist_image_link": d["Artist"].image_link,
           "start_time": d["Show"].start_time
           }
          if da not in data:
             data.append(da)
    except Exception as e:
        flash(str(e))
    
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  if form.validate_on_submit():
    try:
      artist_id = form.artist_id.data
      venue_id = form.venue_id.data
      start_time = form.start_time.data
      
      show = Show(artist_id=artist_id, venue_id= venue_id, start_time=start_time)
     
       
  # on successful db insert, flash success
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
      db.session.close() 
  # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
        db.session.rollback()
        db.session.close()
  # e.g., flash('An error occurred. Show could not be listed.')
        flash('An error occur ' + form.artist_id.data + ' Show could not be listed' + str(e))
  else:
      flash(form.errors)
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
