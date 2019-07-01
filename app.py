import constants


import sys

from flask import Flask
from flask import request
from flask import _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from werkzeug.exceptions import NotFound
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import Unauthorized
from werkzeug.middleware.dispatcher import DispatcherMiddleware


from authenticate import MYSQL_USERNAME,MYSQL_PASSWORD,MYSQL_IP,MYSQL_DB, Auth


main_app = Flask(__name__, static_url_path='/public', static_folder='./public')

from apps import app1, app2, app3

main_app.wsgi_app = DispatcherMiddleware(main_app.wsgi_app, {
    "/{}/app1".format(app1.app.permission): app1.app,
    '/{}/app2'.format(app2.app.permission): app2.app,
    '/{}/app3'.format(app3.app.permission): app3.app
})


main_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(MYSQL_USERNAME,MYSQL_PASSWORD,MYSQL_IP,MYSQL_DB)
main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(main_app)
db.init_app(main_app)

main_app.config.from_object(__name__)
main_app.secret_key = constants.SECRET_KEY
#main_app.debug = True
#SESSION_TYPE='filesystem'
#SESSION_PERMANENT=False
#Session(main_app) #supports for Server-side Session. Optional

auth = Auth(main_app)


from routes import *
from models import *


@main_app.shell_context_processor
def make_shell_context():
    """
    Run `FASK_APP=app.py; flask shell` for an interpreter with local structures.
    """
    return {'db': db, 'User': models.User}