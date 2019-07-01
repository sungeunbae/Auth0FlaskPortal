""" Constants file for Auth0's seed project
"""
AUTH0_CLIENT_ID = 'AUTH0_CLIENT_ID'
AUTH0_CLIENT_SECRET = 'AUTH0_CLIENT_SECRET'
AUTH0_CALLBACK_URL = 'AUTH0_CALLBACK_URL'
AUTH0_DOMAIN = 'AUTH0_DOMAIN'
AUTH0_AUDIENCE = 'AUTH0_AUDIENCE'
PROFILE_KEY = 'profile'
SECRET_KEY = 'ThisIsTheSecretKey'
JWT_PAYLOAD = 'jwt_payload'
MYSQL_USERNAME='MYSQL_USERNAME'
MYSQL_PASSWORD='MYSQL_PASSWORD'
MYSQL_IP='MYSQL_IP'
MYSQL_DB='MYSQL_DB'


JWT_ALGORITHM = "RS256"
JWT_PAYLOAD = 'jwt_payload'
JWT_VERIFY_DEFAULTS = {
    'verify_signature': True,
    'verify_aud': True,
    'verify_iat': True,
    'verify_exp': True,
    'verify_nbf': True,
    'verify_iss': True,
    'verify_sub': True,
    'verify_jti': True,
    'verify_at_hash': True,
    'leeway': 0,
}

TOKEN_KEY = 'auth0_token'
MGMNT_API_TOKEN = 'mgmnt_api_token'