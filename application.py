import datetime
import random
import string
import httplib2
import requests
import json

from flask import Flask, render_template, request, redirect, jsonify, url_for,\
    session as login_session, make_response, flash, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Udacity Catalog Project'

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/catalog.json')
def get_all_catalog_json():
    """JSON endpoint for fetching all catalog details in the database.

        Returns:
            A JSON of all categories and items in the database.
    """
    category_json = []
    try:
        fetch_categories = session.query(Category).all()
        for current_category in fetch_categories:
            fetched_items = session.query(
                Item).filter_by(category_id=current_category.id).all()
            items_json = []
            for current_item in fetched_items:
                item_serialized = current_item.serialize
                item_serialized['email'] = current_item.user.email
                items_json.append(item_serialized)
            current_category_json = {
                'category_name': current_category.name,
                'category_id': current_category.id,
                'items': items_json
            }
            category_json.append(current_category_json)
    except Exception as e:
        error_json = {
            'result': 'No catalog data',
            'error': str(e)
        }
        category_json.append(error_json)
    return jsonify(category_json)


@app.route('/item/<int:item_id>/detail.json')
def get_item_json(item_id):
    """JSON endpoint for fetching item details.

    Args:
        item_id: unique item id.

    Returns:
        A JSON of an item from the database.
    """
    item_json = {}
    try:
        fetched_item = session.query(Item).filter_by(id=item_id).one()
        item_json['category_name'] = fetched_item.category.name
        item_json['category_id'] = fetched_item.category_id
        item_json['detail'] = fetched_item.serialize
        item_json['detail']['email'] = fetched_item.user.email
    except Exception as e:
        item_json['result'] = 'No data for item_id: ' + str(item_id)
        item_json['error'] = str(e)
    return jsonify(item_json)


@app.route('/login')
def show_login():
    """Route for login.

    Returns:
        Login page - login.html.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()

    # return "The current session state is %s" % login_session['state']
    return render_template('views/login.html', STATE=state, categories=categories)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Authenticates user using Google OAuth.

    Returns:
        HTML for login success.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print "data from oauth: " + str(data)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = get_user(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src=\"'
    output += login_session['picture']
    output += ' \" ' \
              'style = \"width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;\"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Log the user out of application.

    Revoke current user token and clear the session.
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('show_login'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def show_categories():
    """Show all categories and 10 most recent items added.

    Returns:
        Landing page - catalog.html.
    """
    categories = session.query(Category).all()
    latest_items = session.query(
        Item).order_by(Item.created_date.desc()).limit(10).all()
    return render_template(
        'views/catalog.html',
        categories=categories,
        latest_items=latest_items,
        is_logged_in=is_logged_in())


@app.route('/catalog/<int:category_id>/items')
def show_items(category_id):
    """Show list of items from a category.

    Args:
        category_id: unique category id.

    Returns:
        items for a category page - items.html.
    """
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template(
        'views/items.html',
        items=items,
        current_category=category,
        categories=categories)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def show_description(category_id, item_id):
    """Show item description.

    Args:
        category_id: unique category id.
        item_id: unique item id.

    Returns:
        item details page - detail.html.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    is_show = is_logged_in() and is_correct_user(item.user_id)
    return render_template(
        'views/detail.html',
        item=item,
        category=category,
        categories=categories,
        show_button=is_show)


@app.route('/catalog/add', methods=['POST', 'GET'])
def add_item():
    """Add an item.

    Returns:
        GET: add an item page - add.html.
        POST: redirect to item details page for item added.
    """
    if not is_logged_in():
        return redirect(url_for('show_login'))

    if request.method == 'POST':
        # extract input values from form and add new item to database
        new_item = Item(
            category_id=int(request.form['category']),
            name=request.form['name'],
            description=request.form['description'],
            created_date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        return redirect(
            url_for(
                'show_description',
                category_id=new_item.category_id,
                item_id=new_item.id))
    else:
        # show add item page
        categories = session.query(Category).all()
        return render_template('views/add.html', categories=categories)


@app.route('/catalog/<int:item_id>/edit', methods=['POST', 'GET'])
def edit_item(item_id):
    """Edit an item.

    Args:
        item_id: unique item id.

    Returns:
        GET: edit item page - edit.html.
        POST: redirect to item details page for edited item.
    """
    if not is_logged_in():
        return redirect(url_for('show_login'))
    edited_item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':
        # extract input values from form and update item in database
        if request.form['category']:
            edited_item.category_id = request.form['category']
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        edited_item.updated_date = datetime.datetime.now()
        session.add(edited_item)
        session.commit()
        return redirect(
            url_for(
                'show_description',
                category_id=edited_item.category_id,
                item_id=edited_item.id))
    else:
        # show edit item page
        categories = session.query(Category).all()
        return render_template(
            'views/edit.html',
            edited_item=edited_item,
            categories=categories)


@app.route('/catalog/<int:item_id>/delete', methods=['POST', 'GET'])
def delete_item(item_id):
    """delete an item.

    Args:
        item_id: unique item id.

    Returns:
        GET: delete an item page - delete.html.
        POST: redirect to show items for a category page.
    """
    if not is_logged_in():
        return redirect(url_for('show_login'))

    item_to_delete = session.query(Item).filter_by(id=item_id).one()
    category_id = item_to_delete.category_id
    categories = session.query(Category).all()

    if request.method == 'POST':
        # Delete item from database and redirect to previous category
        session.delete(item_to_delete)
        session.commit()
        return redirect(
            url_for('show_items', category_id=category_id))
    else:
        # show delete an item page
        return render_template(
            'views/delete.html',
            item_to_delete=item_to_delete,
            category_id=category_id,
            categories=categories)


def get_user(email):
    """Get a user from database.

    Args:
        email: an email for a user.

    Returns:
        a user that has the email given.
    """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as e:
        print 'User not found with the given email ' + email + ': ' + str(e)
        return None


def create_user(current_session):
    """Create a user.

    Args:
        current_session: The current Flask session containing user info.

    Returns:
        user id of newly created user.
    """
    user = User(
                name=current_session['username'],
                email=current_session['email'])
    session.add(user)
    session.flush()
    session.commit()
    return user.id


def is_correct_user(user_id):
    """Check if user id is same as in session.

    Args:
        user_id: unique user id.

    Returns:
        boolean flag if login session user id is same as provided user id.
    """
    return user_id == login_session['user_id']


def is_logged_in():
    """Check if user id is in session.

    Returns:
        boolean flag if user id in session.
    """
    return 'user_id' in login_session

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
