import constants
from os import environ as env
from dotenv import load_dotenv, find_dotenv
from authlib.client import OAuth2Session
from authlib.flask.client import OAuth
from jose import JWTError, jwt
from functools import wraps
from flask import session
from six.moves.urllib.request import urlopen

import json



ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

MYSQL_USERNAME = env.get(constants.MYSQL_USERNAME)
MYSQL_PASSWORD = env.get(constants.MYSQL_PASSWORD)
MYSQL_IP = env.get(constants.MYSQL_IP)
MYSQL_DB = env.get(constants.MYSQL_DB)

SCOPE = 'openid profile '# groups roles permissions read:eaonly read:devonly' #we don't need to request all these scopes. All scopes authorized for the user is auto-added by the rule created by (*) above.


ISSUER = "https://"+AUTH0_DOMAIN+"/"
#Needs API setup  https://auth0.com/docs/quickstart/backend/python#validate-access-tokens




class Auth:
    def __init__(self, app):
        oauth = OAuth(app)
        self.auth0 = oauth.register(
            'auth0',
            client_id=AUTH0_CLIENT_ID,
            client_secret=AUTH0_CLIENT_SECRET,
            api_base_url=AUTH0_BASE_URL,
            access_token_url=AUTH0_BASE_URL + '/oauth/token',
            authorize_url=AUTH0_BASE_URL + '/authorize',
            client_kwargs={
                'scope': SCOPE
            },
        )








# @main_app.errorhandler(Exception)
# def handle_auth_error(ex):
#     response = jsonify(message=str(ex))
#     response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
#     return response



def fetch_mgmnt_api_token():
    __session = OAuth2Session(AUTH0_CLIENT_ID,AUTH0_CLIENT_SECRET) #need a new session to get the token for Mgmnt API
    token = __session.fetch_access_token(AUTH0_BASE_URL + '/oauth/token', grant_type='client_credentials', audience=auth0.api_base_url +'/api/v2/')

    #Alternatively, can use the routine below...
    # conn = http.client.HTTPSConnection("seistech.auth0.com:443")
    # payload = "grant_type=client_credentials&client_id="+AUTH0_CLIENT_ID+"&client_secret="+AUTH0_CLIENT_SECRET+"&audience="+auth0.api_base_url+"/api/v2/"
    # headers = { 'content-type': "application/x-www-form-urlencoded" }
    # conn.request("POST", "https://seistech.auth0.com/oauth/token", payload, headers)
    # res = conn.getresponse()
    # token = res.read().decode("utf-8")
    print(token)
    return token['access_token'] #ok to use it without validation


def __decode_token(token):
#    print("Gonna print the token:", file=sys.stdout)
#    print(jwt.get_unverified_header(token), file=sys.stdout)
#    print(jwt.get_unverified_claims(token), file=sys.stdout)

    jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise(e)
    if unverified_header["alg"] == "HS256":
        raise Exception({"code": "invalid_header",
                         "description":
                             "Invalid header. "
                             "Use an RS256 signed JWT Access Token"}, 401)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }


    if rsa_key:
        try:
            #this verifies everything. 
            payload = jwt.decode(token, rsa_key, algorithms=[constants.JWT_ALGORITHM], issuer=ISSUER, audience=AUTH0_AUDIENCE, options = constants.JWT_VERIFY_DEFAULTS)
        except jwt.ExpiredSignatureError:
            raise Exception({"code":"token_expired",
                             "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise Exception({"code": "invalid_claims",
                             "description":
                                 "incorrect claims,"
                                 " please check the audience and issuer"}, 401)
        except JWTError as e:
            six.raise_from(Unauthorized, e)
        except Exception as e:
            raise Exception({"code": "invalid_header",
                             "description":
                                 "Unable to parse authentication"
                                 " token or unable to decode."}, 401)
    else:
        raise Exception({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return payload # Not sure if signature must be still validated..


def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    print(required_scope)
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = session[constants.TOKEN_KEY]["access_token"]
            unverified_claims = jwt.get_unverified_claims(token)
            print(unverified_claims)
            if unverified_claims.get("scope"):
                token_scopes = unverified_claims["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            raise Exception({"code": "Unauthorized", "description": "You don't have access to this resource"},403)
            
        return decorated
    return require_scope


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.JWT_PAYLOAD not in session:
            return redirect('/login')
        token = session[constants.TOKEN_KEY]
        token_decoded = __decode_token(token["access_token"])
       # _request_ctx_stack.top.current_user = token_decoded #not sure about this one - seems unnecessary.
        return f(*args, **kwargs)

    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session[constants.TOKEN_KEY]["access_token"]
#           print(token)
        unverified_claims = jwt.get_unverified_claims(token)
        print(unverified_claims)
        if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == "admin":
                    mgmnt_token = session.get(constants.MGMNT_API_TOKEN,None)
                    if mgmnt_token is None:
                        session[constants.MGMNT_API_TOKEN] = fetch_mgmnt_api_token()
                    print(session[constants.MGMNT_API_TOKEN])
                    return f(*args, **kwargs)
        raise Exception({"code": "Unauthorized", "description": "You don't have access to this resource"},403)
    return decorated



