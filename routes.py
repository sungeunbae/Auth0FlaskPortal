
from six.moves.urllib.parse import urlencode

# from urllib.parse import urlencode
import six

from flask_cors import cross_origin
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

import json
from main import flask_portal
from authenticate import Auth

from models import get_user_id

from werkzeug.exceptions import HTTPException

from constants import JWT_PAYLOAD, TOKEN_KEY, MGMNT_API_TOKEN

# Controllers API
@flask_portal.app.route("/")
def home():
    return render_template("home.html")


@flask_portal.app.route("/callback")
def callback_handling():
    token = flask_portal.auth.auth0.authorize_access_token()
    resp = flask_portal.auth.auth0.get("userinfo")
    userinfo = resp.json()

    session[JWT_PAYLOAD] = userinfo
    session[TOKEN_KEY] = token
    print(token)
    user_id = get_user_id()

    # this_user = dbsession.query(User).filter_by(id=user_id).first()
    # try:
    #     print("Auth0 id {} DB id {}".format(user_id, this_user.id))
    # except:
    #     print("This user has no info in DB")

    return redirect("/dashboard")


@flask_portal.app.route("/login")
def login():
    return flask_portal.auth.auth0.authorize_redirect(
        redirect_uri=Auth.AUTH0_CALLBACK_URL, audience=Auth.AUTH0_AUDIENCE
    )


@flask_portal.app.route("/logout")
def logout():
    try:
        session.clear()
    except RuntimeError:
        raise Exception("Error: no session present.")
    if flask_portal.dbsession.is_active:
        flask_portal.dbsession.rollback()  # TODO: we should also rollback if there was an exception...

    params = {
        "returnTo": url_for("home", _external=True),
        "client_id": Auth.AUTH0_CLIENT_ID,
    }
    return redirect(
        flask_portal.auth.auth0.api_base_url + "/v2/logout?" + urlencode(params)
    )



@flask_portal.app.route("/dashboard")
@Auth.requires_auth
def dashboard():
    access_level = flask_portal.auth.get_access_level()
    filtered_apps_endpoints = [
        (ep, acl, name)
        for (ep, acl, name) in flask_portal.all_apps_endpoints
        if acl in access_level
    ]
    def __translate_access_level(access_level):
        user_level = ""
        if "admin" in access_level:
            user_level += "Devel/Admin"
        elif "ea" in access_level:
            user_level += "Early Adopter"
        else:
            user_level += "Paid User"
        return user_level

    priv_string = __translate_access_level(access_level)
    return render_template(
        "dashboard.html",
        userinfo=session[JWT_PAYLOAD],
        #userinfo_pretty=json.dumps(priv_string, indent=4),
        accesslevel=priv_string,
        products=filtered_apps_endpoints,
    )


@flask_portal.app.route("/api/public")
def public():
    """No access token required to access this route
    """
    response = (
        "Hello from a public endpoint! You don't need to be authenticated to see this."
    )
    return jsonify(message=response)


@flask_portal.app.route("/api/private")
@Auth.requires_auth
def private():
    """A valid access token is required to access this route
    """
    response = (
        "Hello from a private endpoint! You need to be authenticated to see this."
    )
    return jsonify(message=response)


@flask_portal.app.route("/api/eaonly")
@Auth.requires_scope("ea")
def read_eaonly():
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello!" + get_user_id() + " is authorized to read ea only contents"
    return jsonify(message=response)


@flask_portal.app.route("/api/devonly")
@Auth.requires_scope("devel")
def read_devonly():
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello! You are authorized to read devonly contents"
    return jsonify(message=response)


@flask_portal.app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@flask_portal.app.errorhandler(500)
def internal_error(error):
    flask_portal.dbsession.rollback()
    return render_template("500.html"), 500


@flask_portal.app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(str(ex))
    response.status_code = ex.code if isinstance(ex, HTTPException) else 500
    return response
