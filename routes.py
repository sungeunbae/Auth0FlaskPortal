
from six.moves.urllib.parse import urlencode

#from urllib.parse import urlencode
import six

from flask_cors import cross_origin
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

import json
from main import main_app, auth, all_apps_endpoints
from authenticate import Auth

from models import dbsession, get_user_id

from constants import JWT_PAYLOAD, TOKEN_KEY, MGMNT_API_TOKEN
# Controllers API
@main_app.route('/')
def home():
    return render_template('home.html')


@main_app.route('/callback')
def callback_handling():
    token = auth.auth0.authorize_access_token()
    resp = auth.auth0.get('userinfo')
    userinfo = resp.json()

    session[JWT_PAYLOAD] = userinfo 
    session[TOKEN_KEY] = token
    user_id = get_user_id()

    # this_user = dbsession.query(User).filter_by(id=user_id).first()
    # try:
    #     print("Auth0 id {} DB id {}".format(user_id, this_user.id))
    # except:
    #     print("This user has no info in DB")

    return redirect('/dashboard')


@main_app.route('/login')
def login():
    return auth.auth0.authorize_redirect(redirect_uri=Auth.AUTH0_CALLBACK_URL, audience=Auth.AUTH0_AUDIENCE)


@main_app.route('/logout')
def logout():
    try:
        session.clear()
    except RuntimeError:
        raise Exception("Error: no session present.")
    if dbsession.is_active:
        dbsession.rollback() #TODO: we should also rollback if there was an exception...

    params = {'returnTo': url_for('home', _external=True), 'client_id': Auth.AUTH0_CLIENT_ID}
    return redirect(auth.auth0.api_base_url + '/v2/logout?' + urlencode(params))

def __translate_access_level(access_level):
    user_level = "User level: "     
    if 'admin' in access_level:
        user_level += "Almighty Admin"
    elif 'ea' in access_level:
        user_level += "Early Adopter"
    else:
        user_level += "Paid User"
    return user_level

@main_app.route('/dashboard')
@Auth.requires_auth
def dashboard():
    access_level=auth.get_access_level()
    filtered_apps_endpoints = [(ep,acl,name) for (ep,acl,name) in all_apps_endpoints if acl in access_level]
    priv_string = __translate_access_level(access_level)
    return render_template('dashboard.html',
                           userinfo=session[JWT_PAYLOAD],
                           userinfo_pretty=json.dumps(priv_string, indent=4), products=filtered_apps_endpoints)

@main_app.route("/api/public")
def public():
    """No access token required to access this route
    """
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return jsonify(message=response)

@main_app.route("/api/private")
@Auth.requires_auth
def private():
    """A valid access token is required to access this route
    """
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return jsonify(message=response)

@main_app.route("/api/eaonly")
@Auth.requires_scope('ea')
def read_eaonly():
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello!"+get_user_id()+ " is authorized to read ea only contents"
    return jsonify(message=response)

@main_app.route("/api/devonly")
@Auth.requires_scope('devel')
def read_devonly():
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello! You are authorized to read devonly contents"
    return jsonify(message=response)



