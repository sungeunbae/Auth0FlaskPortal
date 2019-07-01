import http.client
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
from app import main_app, auth
from authenticate import requires_auth, requires_scope, requires_admin, AUTH0_CALLBACK_URL, AUTH0_AUDIENCE, AUTH0_CLIENT_ID, AUTH0_DOMAIN 

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
    return auth.auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@main_app.route('/logout')
def logout():
    session.clear()
    if dbsession.is_active:
        dbsession.rollback() #TODO: we should also rollback if there was an exception...

    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
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
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session[JWT_PAYLOAD],
                           userinfo_pretty=json.dumps(session[JWT_PAYLOAD], indent=4))




@main_app.route("/api/public")
@cross_origin(headers=["Content-Type", "Authorization"])
def public():
    """No access token required to access this route
    """
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return jsonify(message=response)

@main_app.route("/api/private")
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def private():
    """A valid access token is required to access this route
    """
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return jsonify(message=response)

@main_app.route("/api/eaonly")
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
@requires_scope('read:eaonly')
def read_eaonly():
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello!"+get_user_id()+ " is authorized to read ea only contents"
    return jsonify(message=response)

@main_app.route("/api/devonly")
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
@requires_scope('read:devonly')
def read_devonly():
    """A valid access token and an appropriate scope are required to access this route
    """

    response = "Hello! You are authorized to read devonly contents"
    return jsonify(message=response)

@main_app.route("/api/admin")
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
@requires_admin
def read_admin():
    """A valid access token and an appropriate scope are required to access this route
    """
    return render_template('dashboard.html',
                           userinfo=session[MGMNT_API_TOKEN],
                           userinfo_pretty=json.dumps(session[MGMNT_API_TOKEN], indent=4))


##this enables direct access to management API's endpoints. https://auth0.com/docs/api/management/v2 
@main_app.route("/api/admin/<path:subpath>", methods=['GET'])
#@cross_origin(headers=["Content-Type", "Authorization"])
#@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
@requires_admin
def get_request_management_api(subpath):
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN+":443")
    headers = { "Authorization":"Bearer "+session[MGMNT_API_TOKEN], 'content-type' : "application/json"}
    conn.request("GET", auth.auth0.api_base_url+"/api/v2/"+subpath, headers= headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return render_template('dashboard.html',
                           userinfo=data,
                           userinfo_pretty=json.dumps(json.loads(data), indent=4))