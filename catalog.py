#!/bin/python3

import json
import os
import random
import string
import uuid
from functools import wraps
from glob import glob
from os.path import dirname, join, realpath

from database_setup import Base, Category, Sport, User
from flask import (Flask, Response, abort, flash, jsonify, make_response,
                   redirect, render_template, request, send_from_directory)
from flask import session as login_session
from flask import url_for
from flask_thumbnails import Thumbnail
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.functions import func
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8zsdfjsdfhzeKOIJEyhieudpsi\n\xec]/'

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sport Catalog Application"


# flask_thumbnails config
THUMBNAIL_MEDIA_ROOT = join(dirname(realpath(__file__)), 'static/uploads/')
THUMBNAIL_MEDIA_URL = 'media/'

# Upload file config
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# flask_thumbnails init
thumb = Thumbnail(app)

'''Helper class
Manages regex based routes
'''


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


'''
login required wrapper function
'''


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session.get('email') is None:
            flash("You need to Sign in to view this page", "danger")
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


app.url_map.converters['regex'] = RegexConverter
app.config['THUMBNAIL_MEDIA_ROOT'] = THUMBNAIL_MEDIA_ROOT
app.config['THUMBNAIL_MEDIA_URL'] = THUMBNAIL_MEDIA_URL
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DB config and init
engine = create_engine('sqlite:///sports.db',
                       convert_unicode=True,
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool, echo='debug')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

########################################################
# Start of Login related mothods
########################################################

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


'''
google Updated version of sign in API
https://developers.google.com/identity/sign-in/web/backend-auth
https://developers.google.com/identity/sign-in/web/quick-migration-guide#migrate_an_html_sign-in_button
'''

'''Modified version of disconnect
The provided version in the udacity course doesn't work anymore
I use   var auth2 = gapi.auth2.getAuthInstance();
        auth2.signOut()....
from javascript to call this function
'''


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    if login_session.get('user_id'):
        del login_session['user_id']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    flash("Successfully disconnected.", 'info')
    response.headers['Content-Type'] = 'application/json'
    return response


'''Modified version of gconnect
Google have dropped support for google+ sign in and profieded a new api
first in the html I use class="g-signin2" button
and data-onsuccess="onSignIn" when successfully signed in
then from within I make an ajax call and pass the id_token
this id_token when decoded gives user profile info as json
'''


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    token = request.data

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            response = make_response(json.dumps(
                "Could not verify audience."), 401)
            print("Could not verify audience.")

# ID token is valid.
# Get the user's Google Account ID from the decoded token.
        username = idinfo['name']
        useremail = idinfo['email']
        userpicture = idinfo['picture']

    except ValueError:
        # Invalid token
        response = make_response(json.dumps("Invalid token."), 401)
        print("Invalid token.")

    login_session['username'] = username
    login_session['picture'] = userpicture
    login_session['email'] = useremail

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(useremail)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s." %
          login_session['username'], 'success')
    print("done!")
    return output


########################################################
# End of Login related mothods
########################################################

########################################################
# User Helper Functions
########################################################

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    user = session.query(User).filter_by(email=email).one()
    return user.id if user is not None else None


########################################################
# Start of JSON API
########################################################
'''JSON METHOD: All Elements

serialize two joined tables
same raw query as session.query(Category,Sport).all()
but this one doesn't work => error: serializable object not found in result ???
solution: https://stackoverflow.com/questions/50011349/
return-joined-tables-in-json-format-with-sqlalchemy-and-flask-jsonify
'''


@app.route('/api/JSON')
def getAllJSON():
    catalog = session.query(Category).options(
        joinedload(Category.sports)).all()
    return jsonify(Catalog=[dict(c.serializable,
                                 sports=[i.serializable for i in c.sports])
                            for c in catalog])

########################################################
# End of JSON API
########################################################


'''
Query database for all categories and the count of sports in each one
and latest 5 added sports
returns: home page
'''


@app.route('/')
@app.route('/catalog')
def index():
    # get all categories and the count of sports in each one
    # https://stackoverflow.com/a/39053724/6007152
    categories_count = session.query(Category.name, func.count(
        Sport.id)).outerjoin(Sport).group_by(Category.id).all()
    sports = session.query(Sport).order_by(Sport.id.desc()).limit(5)
    if login_session.get('email') is None:
        return render_template('public_index.html',
                               categories=categories_count,
                               sports=sports,
                               STATE=login_session.get('state'))
    return render_template('index.html',
                           categories=categories_count,
                           sports=sports,
                           STATE=login_session.get('state'))


########################################################
# Start of Category related routes
########################################################

'''
Query database for a specific category and
return list of sports in that category
returns: category page
'''


@app.route('/catalog/<string:category_name>/')
def categories(category_name):
    category = session.query(Category).filter_by(
        name=category_name.lower()).first()
    if not category:
        flash(u'Categoty %s not found' % category_name, 'danger')
        return redirect(url_for('index'))
    sports = session.query(Sport).filter_by(
        category_id=category.id).order_by(Sport.id.desc())
    if login_session.get('email') is None:
        return render_template('public_categories.html',
                               sports=sports,
                               category=category,
                               STATE=login_session.get('state'))
    return render_template('categories.html',
                           sports=sports,
                           category=category,
                           STATE=login_session.get('state'))


@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        if request.form.get('categoryName'):
            category_name = request.form['categoryName'].strip().lower()
            category = Category(name=category_name,
                                user_id=login_session['user_id'])
        else:
            flash(u'Category name is required', 'danger')
            return redirect(url_for('newCategory'))
        try:
            session.add(category)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash(u'Category %s already exists' % category.name, 'danger')
            return redirect(url_for('newCategory'))
        flash(u'Category %s added succesfully' % category.name, 'success')
        return redirect(url_for('index'))
    return render_template('newcategory.html',
                           STATE=login_session.get('state'))


@app.route('/catalog/<string:category_name>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    category = session.query(Category).filter_by(
        name=category_name.lower()).first()
    if request.method == 'POST':
        if request.form['categoryName']:
            category.name = request.form['categoryName'].strip().lower()
            try:
                session.add(category)
                session.commit()
            except exc.IntegrityError:
                session.rollback()
                flash(u'Category %s already exists' % category.name, 'danger')
                return redirect(url_for('editCategory',
                                        category_name=category_name.lower()))
            flash(u'Category %s edited succesfully' % category.name, 'success')
            return redirect(url_for('categories',
                                    category_name=category.name))
    return render_template('editcategory.html',
                           category=category,
                           STATE=login_session.get('state'))


'''[Delete a category]
All sports within this category will be moved to the
Uncategorized category (fallback)
'''


@app.route('/catalog/<string:category_name>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    category = session.query(Category).filter_by(
        name=category_name.lower()).first()
    if request.method == 'POST':
        sports = session.query(Sport).filter_by(category_id=category.id).all()
        for sport in sports:
            sport.category_id = 1
            session.add(sport)
        session.delete(category)
        session.commit()
        flash(u'Category %s deleted succesfully' % category.name, 'success')
        return redirect(url_for('index'))
    return render_template('deletecategory.html',
                           category=category,
                           STATE=login_session.get('state'))

########################################################
# End of Category related routes
########################################################

########################################################
# Start of Sports related routes
########################################################


@app.route('/catalog/<string:category_name>/<string:sport_name>')
def sports(category_name, sport_name):
    sport = session.query(Sport).filter_by(name=sport_name.lower()).first()
    if not sport:
        flash(u'Sport %s not found' % sport_name, 'danger')
        return redirect(url_for('index'))
    if login_session.get('email') is None:
        return render_template('public_sports.html',
                               sport=sport,
                               STATE=login_session.get('state'))
    return render_template('sports.html',
                           sport=sport,
                           STATE=login_session.get('state'))


'''add route with optional param
if the view is lanched from category view => the actual category is passed
'''


@app.route('/catalog/<string:category_name>?/sports/new/', methods=['GET',
                                                                    'POST'])
@app.route('/catalog/sports/new/', methods=['GET', 'POST'])
@login_required
def newSport(category_name=None):
    if request.method == 'POST':
        category = None
        if request.form.get('sportCategory'):
            category = session.query(Category).filter_by(
                id=request.form['sportCategory'].lower()).first()
        if not category:
            category = session.query(Category).filter_by(
                id=1).first()
        if not request.form.get('sportName'):
            return "sportName required"
        sport = Sport(name=request.form.get('sportName').strip().lower(),
                      description=request.form.get('sportDescription'),
                      category_id=category.id,
                      user_id=login_session['user_id'])
        # check if the post request has the file part
        # Image upload is optional
        if 'sportImage' not in request.files:
            file = None
        else:
            file = request.files['sportImage']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file and allowed_file(file.filename) and file.filename != '':
            filename = secure_filename(
                "".join([str(uuid.uuid4()), "_", file.filename]))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sport.image = filename
        if file and file.filename == '':
            sport.image = ''
        try:
            session.add(sport)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash(u'Sport %s already exists' % sport.name, 'danger')
            return redirect(url_for('newSport'))
        flash(u'Sport %s successfully added' % sport.name, 'success')
        return redirect(url_for('categories',
                                category_name=sport.category.name))
    categories = session.query(Category).filter(Category.id != 1).all()
    return render_template('newsport.html',
                           categories=categories,
                           category_name=category_name,
                           STATE=login_session.get('state'))


'''Edit a sport
When a new image is supplied
 it will replace the existing image => image filename wont change
'''


@app.route('/catalog/<string:category_name>/<string:sport_name>/edit/',
           methods=['GET', 'POST'])
@login_required
def editSport(category_name, sport_name):
    sport = session.query(Sport).filter_by(name=sport_name.lower()).first()

    categories = session.query(Category).filter(Category.id != 1).all()
    if request.method == 'POST':
        category = None
        if request.form.get('sportCategory'):
            category = session.query(Category).filter_by(
                id=request.form['sportCategory'].strip().lower()).first()
        if not category:
            category = session.query(Category).filter_by(
                id=1).first()
        if request.form.get('sportName'):
            sport.name = request.form.get('sportName').strip().lower()
        if request.form.get('sportDescription'):
            sport.description = request.form.get('sportDescription')
        sport.category_id = category.id
        if 'sportImage' not in request.files:
            file = None
        else:
            file = request.files['sportImage']
        if file and allowed_file(file.filename) and file.filename != '':
            filename = file.filename if sport.image == '' else sport.image
            print(filename)
            if sport.image != '':
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],
                                               sport.image)):
                    os.remove(os.path.join(
                        app.config['UPLOAD_FOLDER'], sport.image))
                    del_filename = os.path.splitext(sport.image)[0]
                    for f in glob(os.path.join
                                  (app.config['THUMBNAIL_MEDIA_URL'],
                                   del_filename)+'*.jpg'):
                        os.remove(f)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        try:
            sport.image = filename
            session.add(sport)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash(u'Sport %s already exists' % sport.name, 'danger')
            return redirect(url_for('editSport',
                                    category_name=sport.category.name,
                                    sport_name=sport.name))
        flash(u'Sport %s successfully edited' % sport.name, 'success')
        return redirect(url_for('sports',
                                category_name=sport.category.name,
                                sport_name=sport.name))
    return render_template('editsport.html',
                           categories=categories,
                           sport=sport,
                           STATE=login_session.get('state'))


'''Delete a sport
Delete a sport and its associated image
'''


@app.route('/catalog/<string:category_name>/<string:sport_name>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteSport(category_name, sport_name):
    sport = session.query(Sport).filter_by(name=sport_name.lower()).first()
    if request.method == 'POST':
        if not sport:
            abort(Response('Item not found'))
        session.delete(sport)
        if sport.image != '':
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], sport.image))
        session.commit()
        flash(u'Sport %s successfully Deleted' % sport.name, 'success')
        return redirect(url_for('categories',
                                category_name=category_name))
    return render_template('deletesport.html',
                           sport=sport,
                           STATE=login_session.get('state'))

#############################################
# END OF Sport's routes
#############################################


'''checks if an extension is valid

Returns:
    Boolean: in allowed extensions
'''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


'''Helper filter
This filter is used in combination with flask_thumbnails
 to check if an image exists and return placeholder image if not
Returns:
    [filename]: [image or placeholder_image]
'''


@app.template_filter('exists')
def exists(file):
    exists = os.path.isfile('static/uploads/'+file)
    if exists:
        return file
    return 'placeholder_150.jpg'


'''Helper route
This regex route is used to solve flask_thumbnails bug
(look for images in / directory instead of the difined
THUMBNAIL_MEDIA_URL directory)
Returns:
    [filename]: [correct image path]
'''


@app.route(r'/<regex("([\w\d_/-]+)?.(?:jpe?g|gif|png)"):filename>')
def media_file(filename):
    return send_from_directory(app.config['THUMBNAIL_MEDIA_URL'], filename)


'''Helper route
To upload files
'''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


'''Helper Method to resolve caching issues
Adds required headers to the response object
https://stackoverflow.com/questions/13768007/browser-caching-issues-in-flask
'''


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Cache-Control'] += 'no-cache, '
    response.headers['Cache-Control'] += 'must-revalidate, '
    response.headers['Cache-Control'] += 'max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
