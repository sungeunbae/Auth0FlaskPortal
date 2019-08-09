import constants
import json

from authlib.client import OAuth2Session
from authlib.flask.client import OAuth

from dotenv import load_dotenv, find_dotenv
from functools import wraps
from flask import session
from flask import redirect
from flask import render_template
from jose import JWTError, jwt
from os import environ as env
import six
from six.moves.urllib.request import urlopen
from werkzeug.exceptions import Unauthorized, Forbidden

# from errors import *

# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class Auth:

    ENV_FILE = find_dotenv()
    if ENV_FILE:
        load_dotenv(ENV_FILE)

    AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
    AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
    AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
    AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
    AUTH0_BASE_URL = "https://" + AUTH0_DOMAIN
    AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
    SECRET_KEY = env.get(constants.SECRET_KEY)

    MYSQL_USERNAME = env.get(constants.MYSQL_USERNAME)
    MYSQL_PASSWORD = env.get(constants.MYSQL_PASSWORD)
    MYSQL_IP = env.get(constants.MYSQL_IP)
    MYSQL_DB = env.get(constants.MYSQL_DB)

    SCOPE = (
        "openid profile "
    )  # All scopes authorized for the user are auto-added (without explicit request) by the rule
    # See SPA+API: Auth0 Configuration for more details
    # https://auth0.com/docs/architecture-scenarios/spa-api/part-2

    ISSUER = "https://" + AUTH0_DOMAIN + "/"
    # Needs API setup  https://auth0.com/docs/quickstart/backend/python#validate-access-tokens

    def __init__(self, app):
        self.app = app
        self.auth0 = OAuth(app).register(
            "auth0",
            client_id=Auth.AUTH0_CLIENT_ID,
            client_secret=Auth.AUTH0_CLIENT_SECRET,
            api_base_url=Auth.AUTH0_BASE_URL,
            access_token_url=Auth.AUTH0_BASE_URL + "/oauth/token",
            authorize_url=Auth.AUTH0_BASE_URL + "/authorize",
            client_kwargs={"scope": Auth.SCOPE},
        )

    def get_access_level(self):
        scopes = self.__get_scopes()
        access_level = [x.split("access:")[1] for x in scopes if x.find("access:") >= 0]
        return [
            "stable"
        ] + access_level  # all authenticated users have "stable" access level

    def __get_scopes(self):
        token_scopes = []
        token = Auth.__authenticate_token()
        unverified_claims = jwt.get_unverified_claims(token["access_token"])
        if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
        return token_scopes

    @staticmethod
    def __fetch_mgmnt_api_token():
        __session = OAuth2Session(
            Auth.AUTH0_CLIENT_ID, Auth.AUTH0_CLIENT_SECRET
        )  # need a new session to get the token for Mgmnt API
        token = __session.fetch_access_token(
            Auth.AUTH0_BASE_URL + "/oauth/token",
            grant_type="client_credentials",
            audience=Auth.AUTH0_BASE_URL + "/api/v2/",
        )

        return token["access_token"]  # ok to use it without validation

    @staticmethod
    def __decode_token(token):

        jsonurl = urlopen("https://" + Auth.AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except Exception as e:
            raise (e)
        if unverified_header["alg"] == "HS256":
            raise Exception(
                {
                    "code": "invalid_header",
                    "description": "Invalid header. "
                    "Use an RS256 signed JWT Access Token",
                },
                401,
            )
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        if rsa_key:
            try:
                # this verifies everything.
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[constants.JWT_ALGORITHM],
                    issuer=Auth.ISSUER,
                    audience=Auth.AUTH0_AUDIENCE,
                    options=constants.JWT_VERIFY_DEFAULTS,
                )
            except jwt.ExpiredSignatureError:
                raise Exception(
                    {"code": "token_expired", "description": "token is expired"}, 401
                )
            except jwt.JWTClaimsError:
                raise Exception(
                    {
                        "code": "invalid_claims",
                        "description": "incorrect claims,"
                        " please check the audience and issuer",
                    },
                    401,
                )
            except JWTError as e:
                six.raise_from(Unauthorized, e)
            except Exception as e:
                raise Exception(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authentication"
                        " token or unable to decode.",
                    },
                    401,
                )
        else:
            raise Exception(
                {
                    "code": "invalid_header",
                    "description": "Unable to find appropriate key",
                },
                401,
            )
        return payload

    @staticmethod
    def requires_scope(required_scope):
        """Determines if the required scope is present in the access token
        Args:
            required_scope (str): The scope required to access the resource
        """

        def require_scope(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = Auth.__authenticate_token()
                if token is None:
                    return redirect("/login")  # if not even authenticated,
                unverified_claims = jwt.get_unverified_claims(token["access_token"])
                if unverified_claims.get("scope"):
                    token_scopes = unverified_claims["scope"].split()
                    for token_scope in token_scopes:
                        if token_scope == required_scope:
                            return f(*args, **kwargs)
                # raise Exception({"code": "Unauthorized", "description": "You don't have access to this resource"},403)
                # render_template("404.html", error = str(e))
                six.raise_from(Forbidden, Exception(403))

            return decorated

        return require_scope

    @staticmethod
    def __authenticate_token():
        if constants.JWT_PAYLOAD not in session:
            return None
        token = session[constants.TOKEN_KEY]
        Auth.__decode_token(token["access_token"])
        return token

    @staticmethod
    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = Auth.__authenticate_token()
            if token is None:
                return redirect("/login")
            # _request_ctx_stack.top.current_user = token_decoded #not sure about this one - seems unnecessary.
            return f(*args, **kwargs)

        return decorated

    @staticmethod
    def requires_admin(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = session[constants.TOKEN_KEY]["access_token"]
            unverified_claims = jwt.get_unverified_claims(token)
            if unverified_claims.get("scope"):
                token_scopes = unverified_claims["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == "access:admin":
                        mgmnt_token = session.get(constants.MGMNT_API_TOKEN, None)
                        if mgmnt_token is None:
                            session[
                                constants.MGMNT_API_TOKEN
                            ] = Auth.__fetch_mgmnt_api_token()

                        return f(*args, **kwargs)
            # raise AuthError({"code": "Forbidden", "description": "You don't have access to this resource"},403)
            six.raise_from(Forbidden, Exception(403))

        return decorated
