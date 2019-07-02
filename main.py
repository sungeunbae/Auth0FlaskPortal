import constants
import sys

from flask import Flask
from flask import request
from flask import _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
#from flask import session

from werkzeug.exceptions import NotFound
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import Unauthorized
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from authenticate import Auth
from apps import *

main_app = Flask(__name__, static_url_path='/public', static_folder='./public')

#collect all legit apps under "apps" directory and create a dictionary having the endpoint (eg. /devel/xxx) as the key.    
all_apps=[(x.split("apps.")[1],sys.modules[x].app) for x in sys.modules.keys() if x.find("apps.")>=0]
all_apps_dict = {}
all_apps_endpoints = []
for app_name, app_obj in all_apps:
    endpoint = "/{}/{}".format(app_obj.permission,app_name)
    all_apps_dict[endpoint]=app_obj
    all_apps_endpoints.append((endpoint,app_obj.permission,app_name))


main_app.wsgi_app = DispatcherMiddleware(main_app.wsgi_app, all_apps_dict)


main_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(Auth.MYSQL_USERNAME,Auth.MYSQL_PASSWORD,Auth.MYSQL_IP,Auth.MYSQL_DB)
main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(main_app)
db.init_app(main_app)

main_app.config.from_object(__name__)
main_app.secret_key = Auth.SECRET_KEY
#main_app.debug = True
#SESSION_TYPE='filesystem'
#SESSION_PERMANENT=False
#Session(main_app) #supports for Server-side Session. Optional

auth = Auth(main_app)


from models import *
from routes import *


@main_app.shell_context_processor
def make_shell_context():
    """
    Run `FASK_APP=app.py; flask shell` for an interpreter with local structures.
    """
    return {'db': db, 'User': models.User}