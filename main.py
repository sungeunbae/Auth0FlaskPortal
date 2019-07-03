import constants
import os.path
import sys

from flask import Flask
from flask import request
from flask import _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
#from flask import session

from importlib import import_module
from pathlib import Path

from werkzeug.exceptions import NotFound
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import Unauthorized
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from authenticate import Auth


main_app = Flask(__name__, static_url_path='/public', static_folder='./public')

#collect all legit apps under "apps" directory and create a dictionary having the endpoint (eg. /devel/xxx) as the key.

modules=[os.path.dirname(x).replace("/",".") for x in Path('apps').glob('**/__init__.py')]

#dynamically import each module discovered
for mod in modules: 
    import_module(mod)
 
 #converting the modules list to dictionary using the access level type as the key.
modules_dict = {}
for actype in constants.ACCESS_LEVELS:
    modules_dict[actype]= [x for x in modules if x.find("apps.{}.".format(actype))>=0]
    modules_dict[actype].sort()

endpoint_app_dict = {}
all_apps_endpoints = []
for actype in modules_dict:
    for app_name in modules_dict[actype]:
        app_obj = sys.modules[app_name].app

        endpoint = '/'+app_name.replace(".","/")
        endpoint_app_dict[endpoint]=app_obj
        all_apps_endpoints.append((endpoint,app_obj.permission,app_name))

print(endpoint_app_dict)

main_app.wsgi_app = DispatcherMiddleware(main_app.wsgi_app, endpoint_app_dict)


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


from models import * #dbSession
from routes import *
from errors import *
  


@main_app.shell_context_processor
def make_shell_context():
    """
    Run `FASK_APP=app.py; flask shell` for an interpreter with local structures.
    """
    return {'db': db, 'User': models.User}