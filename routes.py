
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

    print(token)

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

# the following APIs are only possible if you created the rules for custome claims. 
#@main_app.route('/groups')
#def groups():
#    payload = session[JWT_PAYLOAD]
#    groups = payload.get('http://seistech.nz/claims/groups')
#    response = "groups: "+",".join(groups)
#    return jsonify(message=response)
#
#@main_app.route('/roles')
#def roles():
#    payload = session[JWT_PAYLOAD]
#    roles = payload.get('http://seistech.nz/claims/roles')
#    response = "roles: "+",".join(roles)
#    return jsonify(message=response)
#


@main_app.route('/dashboard')
@Auth.requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session[JWT_PAYLOAD],
                           userinfo_pretty=json.dumps(session[JWT_PAYLOAD], indent=4), products=all_apps_endpoints)




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
#@requires_auth
@Auth.requires_scope('ea')
def read_eaonly():
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello!"+get_user_id()+ " is authorized to read ea only contents"
    return jsonify(message=response)

@main_app.route("/api/devonly")
#@requires_auth
@Auth.requires_scope('devel')
def read_devonly():
    """A valid access token and an appropriate scope are required to access this route
    """

    response = "Hello! You are authorized to read devonly contents"
    return jsonify(message=response)



